import pika
import json
import os
import time
import datetime
import random
import cv2
import numpy as np
from pymongo import MongoClient
import gridfs
from ultralytics import YOLO
import psycopg2
from psycopg2.extras import RealDictCursor
from io import BytesIO

# Configuration from environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/caps")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/caps")

class PrivacyEngine:
    """개인정보 보호를 위한 비식별화(모자이크/블러) 엔진"""
    def __init__(self, mode="blur"):
        self.mode = mode

    def apply(self, frame, detections):
        """
        탐지된 객체(안면, 번호판 등)에 대해 비식별화 적용
        현재는 YOLO 탐지 결과의 class_id나 label을 기반으로 처리
        """
        for det in detections:
            # 0: person, 2: car 등 (COCO dataset 기준)
            # 실제 PRD에서는 안면(Face)과 번호판(License Plate) 전용 모델 사용 권장
            if det['label'] in ['person', 'face', 'license-plate']:
                x1, y1, x2, y2 = map(int, det['bbox'])
                
                # 경계 검사
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                roi = frame[y1:y2, x1:x2]
                if self.mode == "blur":
                    # 블러 처리
                    blurred_roi = cv2.GaussianBlur(roi, (51, 51), 30)
                    frame[y1:y2, x1:x2] = blurred_roi
                else:
                    # 모자이크 처리
                    h, w = roi.shape[:2]
                    temp = cv2.resize(roi, (w//10, h//10), interpolation=cv2.LINEAR)
                    frame[y1:y2, x1:x2] = cv2.resize(temp, (w, h), interpolation=cv2.NEAREST)
        return frame

class AIEngine:
    """YOLOv11 기반 객체 탐지 및 TensorRT 최적화 구조"""
    def __init__(self):
        # TensorRT 최적화 모델 유무 확인 (Phase 1 목표)
        model_path = "yolo11n.pt" # 기본 모델
        trt_path = "yolo11n.engine"
        
        if os.path.exists(trt_path):
            print(f"[*] Loading TensorRT optimized model: {trt_path}")
            self.model = YOLO(trt_path, task='detect')
        else:
            print(f"[*] TensorRT model not found. Using standard model: {model_path}")
            self.model = YOLO(model_path)
            # self.model.export(format='engine') # TensorRT로 내보내기 시도 가능

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            label = self.model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            
            if confidence > 0.4:
                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": bbox
                })
        return detections

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL)

def init_db():
    print("Initializing PostgreSQL table...")
    while True:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    file_id VARCHAR(50) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    analysis_data JSONB,
                    processed_file_id VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("[*] DB initialized.")
            break
        except Exception as e:
            print(f"[!] DB connection failed, retrying in 2 seconds: {e}")
            time.sleep(2)

# AI 엔진 및 프라이버시 엔진 초기화
print("[*] Initializing AI Engines...")
ai_engine = AIEngine()
privacy_engine = PrivacyEngine(mode="blur")

def process_video(file_id, filename):
    print(f"[*] Processing video: {filename} ({file_id})")
    
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client.get_database()
    fs = gridfs.GridFS(db)
    
    try:
        from bson import ObjectId
        grid_out = fs.get(ObjectId(file_id))
        video_data = grid_out.read()
        
        # 임시 파일로 저장하여 OpenCV로 읽기
        temp_input = f"temp_in_{file_id}.mp4"
        temp_output = f"temp_out_{file_id}.mp4"
        with open(temp_input, 'wb') as f:
            f.write(video_data)
        
        cap = cv2.VideoCapture(temp_input)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 결과 비디오 저장을 위한 설정
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
        
        object_counts = {}
        frame_count = 0
        
        print(f"[*] Starting AI analysis and privacy masking...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 1. AI 탐지
            detections = ai_engine.detect(frame)
            
            # 2. 결과 집계 (프레임별)
            for det in detections:
                label = det['label']
                object_counts[label] = object_counts.get(label, 0) + 1
            
            # 3. 비식별화 적용
            frame = privacy_engine.apply(frame, detections)
            
            # 4. 프레임 쓰기
            out.write(frame)
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"[*] Processed {frame_count} frames...")

        cap.release()
        out.release()
        
        # 5. 처리된 영상 MongoDB에 저장
        with open(temp_output, 'rb') as f:
            processed_file_id = fs.put(f, filename=f"processed_{filename}", content_type="video/mp4")
        
        # 6. PostgreSQL에 결과 및 처리된 파일 ID 저장
        summary = {
            "total_frames": frame_count,
            "counts": object_counts,
            "status": "completed"
        }
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO analysis_results (file_id, filename, analysis_data, processed_file_id) VALUES (%s, %s, %s, %s)",
            (file_id, filename, json.dumps(summary), str(processed_file_id))
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # 임시 파일 삭제
        os.remove(temp_input)
        os.remove(temp_output)
        
        print(f"[!] Analysis and masking completed for {filename}")
        
    except Exception as e:
        print(f"[!] Error processing video: {e}")
    finally:
        mongo_client.close()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        process_video(data['file_id'], data['filename'])
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] Callback error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    init_db()
    
    print("[*] Worker starting. Connecting to RabbitMQ...")
    params = pika.URLParameters(RABBITMQ_URL)
    
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='video_analysis_task', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='video_analysis_task', on_message_callback=callback)
            
            print("[*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
        except Exception as e:
            print(f"[!] Connection failed, retrying in 5 seconds: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
