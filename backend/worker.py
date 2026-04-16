import pika
import json
import os
import time
import datetime
import random
from pymongo import MongoClient
import gridfs
# from ultralytics import YOLO  # YOLOv11 대신 모의 분석 사용
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration from environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/caps")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/caps")

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

def process_video(file_id, filename):
    print(f"[*] Processing video: {filename} ({file_id})")
    
    # 1. MongoDB에서 비디오 가져오기
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client.get_database()
    fs = gridfs.GridFS(db)
    
    try:
        from bson import ObjectId
        grid_out = fs.get(ObjectId(file_id))
        # 파일을 실제로 읽어서 처리하는 시뮬레이션
        _ = grid_out.read()
        
        # 2. 모의(Mock) 분석 수행 (YOLO 대신 시뮬레이션)
        print(f"[*] Simulating analysis...")
        time.sleep(3) # 분석 시간 시뮬레이션
        
        # 분석 결과 요약 모의 데이터
        summary = [
            {"person": random.randint(5, 20), "car": random.randint(1, 5)},
            {"person": random.randint(10, 30), "bicycle": random.randint(0, 3)}
        ]
        
        # 3. PostgreSQL에 결과 저장
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO analysis_results (file_id, filename, analysis_data) VALUES (%s, %s, %s)",
            (file_id, filename, json.dumps({"summary": summary, "status": "completed"}))
        )
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[!] Analysis completed for {filename}")
        
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
