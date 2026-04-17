import pika
import json
import os
import time
import datetime
import cv2
import numpy as np
from database import mongo_db, fs, RABBITMQ_URL, SessionLocal, AnalysisResult, init_postgres, cache_set
from ultralytics import YOLO

class PrivacyEngine:
    """개인정보 보호를 위한 비식별화(모자이크/블러) 엔진"""
    def __init__(self, mode="blur"):
        self.mode = mode

    def apply(self, frame, detections):
        for det in detections:
            if det['label'] in ['person', 'face', 'license-plate']:
                x1, y1, x2, y2 = map(int, det['bbox'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                roi = frame[y1:y2, x1:x2]
                if self.mode == "blur":
                    blurred_roi = cv2.GaussianBlur(roi, (51, 51), 30)
                    frame[y1:y2, x1:x2] = blurred_roi
                else:
                    h, w = roi.shape[:2]
                    temp = cv2.resize(roi, (w//10, h//10), interpolation=cv2.LINEAR)
                    frame[y1:y2, x1:x2] = cv2.resize(temp, (w, h), interpolation=cv2.NEAREST)
        return frame

class ContextEngine:
    """기상 정보 및 외부 교통 데이터를 결합하는 멀티모달 엔진"""
    def get_environmental_context(self):
        # 실제 운영 환경에서는 기상청 API 등을 연동하지만, 여기서는 시뮬레이션 데이터를 반환합니다.
        contexts = [
            {"weather": "Clear", "temp": 22, "road_condition": "Dry", "risk_multiplier": 1.0},
            {"weather": "Rainy", "temp": 18, "road_condition": "Wet", "risk_multiplier": 1.3},
            {"weather": "Snowy", "temp": -2, "road_condition": "Icy", "risk_multiplier": 1.5}
        ]
        return np.random.choice(contexts)

class AIEngine:
    def __init__(self):
        model_path = "yolo11n.pt"
        trt_path = "yolo11n.engine"
        if os.path.exists(trt_path):
            print(f"[*] Loading TensorRT optimized model: {trt_path}")
            self.model = YOLO(trt_path, task='detect')
        else:
            print(f"[*] TensorRT model not found. Using standard model: {model_path}")
            self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []
        uncertain_detections = []
        for box in results.boxes:
            label = self.model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            if confidence > 0.4:
                detections.append({"label": label, "confidence": confidence, "bbox": bbox})
            
            # Active Learning: 신뢰도가 낮은(0.4~0.6) 탐지는 별도 플래그 (재학습용)
            if 0.4 <= confidence <= 0.6:
                uncertain_detections.append({"label": label, "confidence": confidence, "bbox": bbox})
                
        return detections, uncertain_detections

# 싱글톤 엔진 초기화
print("[*] Initializing AI Engines...")
ai_engine = AIEngine()
privacy_engine = PrivacyEngine(mode="blur")
context_engine = ContextEngine()

def process_video(file_id, filename):
    print(f"[*] Processing video: {filename} ({file_id})")
    try:
        from bson import ObjectId
        grid_out = fs.get(ObjectId(file_id))
        video_data = grid_out.read()
        
        temp_input = f"temp_in_{file_id}.mp4"
        temp_output = f"temp_out_{file_id}.mp4"
        with open(temp_input, 'wb') as f:
            f.write(video_data)
        
        cap = cv2.VideoCapture(temp_input)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(temp_output, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        
        object_counts = {}
        frame_count = 0
        active_learning_pool = [] # 재학습 대상 데이터 인덱스
        
        # 멀티모달 컨텍스트 획득
        env_context = context_engine.get_environmental_context()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            detections, uncertains = ai_engine.detect(frame)
            for det in detections:
                label = det['label']
                object_counts[label] = object_counts.get(label, 0) + 1
            
            # 액티브 러닝 샘플링 (불확실한 프레임 기록)
            if len(uncertains) > 0 and len(active_learning_pool) < 10:
                active_learning_pool.append({"frame_idx": frame_count, "uncertains": uncertains})
            
            frame = privacy_engine.apply(frame, detections)
            out.write(frame)
            frame_count += 1
            if frame_count % 50 == 0: print(f"[*] Processed {frame_count} frames...")

        cap.release()
        out.release()
        
        total_people = object_counts.get('person', 0)
        avg_people = total_people / frame_count if frame_count > 0 else 0
        
        # 멀티모달 기반 가중치 적용 위험 지수 산출
        density_score = min(avg_people / 20.0, 1.0)
        weather_multiplier = env_context.get('risk_multiplier', 1.0)
        risk_score = min(density_score * weather_multiplier, 1.0)
        
        alerts = []
        if risk_score > 0.7:
             alerts.append({
                 "type": "multi_modal_danger", 
                 "level": "WARNING" if risk_score < 0.9 else "CRITICAL", 
                 "message": f"위험 감지 (인파밀집: {avg_people:.1f}명, 환경: {env_context['weather']})", 
                 "timestamp": datetime.datetime.now().isoformat()
             })

        with open(temp_output, 'rb') as f:
            processed_file_id = fs.put(f, filename=f"processed_{filename}", content_type="video/mp4")
        
        # SQLAlchemy 저장
        db = SessionLocal()
        result_record = AnalysisResult(
            file_id=file_id,
            filename=filename,
            analysis_data={
                "total_frames": frame_count, 
                "counts": object_counts, 
                "risk_score": risk_score, 
                "alerts": alerts,
                "multi_modal_context": env_context,
                "active_learning_candidates": len(active_learning_pool)
            },
            processed_file_id=str(processed_file_id)
        )
        db.add(result_record)
        db.commit()
        db.close()
        
        # Redis 실시간 데이터 업데이트 (Phase 0 / Phase 2 기반)
        latest_data = {
            "filename": filename,
            "counts": object_counts,
            "risk_score": risk_score,
            "timestamp": datetime.datetime.now().isoformat()
        }
        cache_set("latest_analytics", latest_data, expire=300)
        # 결과 목록 캐시 무효화 (다음번 조회 시 DB에서 새로 가져오도록)
        # 여기서는 단순히 만료시키거나 삭제하는 대신 cache_set으로 덮어씌울 수도 있지만,
        # 간단하게 만료 시간을 0으로 주어 삭제 효과를 낼 수도 있습니다. (또는 따로 r.delete() 노출 필요)
        # 현재 cache_set은 ex=expire를 사용하므로 0을 주면 바로 만료될 수 있습니다.
        cache_set("all_results_latest", None, expire=0)
        
        os.remove(temp_input)
        os.remove(temp_output)
        print(f"[!] Analysis completed for {filename}")
    except Exception as e:
        print(f"[!] Error: {e}")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        process_video(data['file_id'], data['filename'])
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] Callback error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    init_postgres()
    print("[*] Worker starting. Connecting to RabbitMQ...")
    params = pika.URLParameters(RABBITMQ_URL)
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='video_analysis_task', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='video_analysis_task', on_message_callback=callback)
            print("[*] Waiting for messages...")
            channel.start_consuming()
        except Exception as e:
            print(f"[!] Retrying in 5s: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
