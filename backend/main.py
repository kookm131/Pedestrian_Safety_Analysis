from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import datetime
import random
import os
import pika
import json
from pymongo import MongoClient
import gridfs

app = FastAPI(title="CAPS Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zero Trust Security: JWT Auth Middleware
from fastapi import Request
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 공개 API 제외 (데모 목적상 현재는 패스)
    if request.url.path in ["/api/status", "/docs", "/openapi.json"]:
        return await call_next(request)
        
    # auth_token 확인 (데모용 헤더 로닉)
    # 실제로는 Identity Provider(Keycloak, Google Auth 등) 연동 권장
    auth_header = request.headers.get("Authorization")
    if not auth_header and os.getenv("STRICT_AUTH", "false") == "true":
         raise HTTPException(status_code=401, detail="Unauthorized")
         
    return await call_next(request)

# Configuration from environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/caps")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# MongoDB & GridFS setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.get_database()
fs = gridfs.GridFS(db)

# RabbitMQ helper
def publish_message(message: dict):
    try:
        # Parse connection URL
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='video_analysis_task', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='video_analysis_task',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        return True
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")
        return False

class Device(BaseModel):
    id: str
    location: str
    status: str
    object_count: int

@app.get("/api/status")
async def get_status():
    return {"status": "정상", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # 1. MongoDB GridFS에 저장
        file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
        
        # 2. 업로드 내역 정보 구성
        upload_info = {
            "file_id": str(file_id),
            "filename": file.filename,
            "upload_at": datetime.datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # 3. RabbitMQ 메시지 발행
        if publish_message(upload_info):
            return {"message": "업로드 성공 및 분석 요청 완료", "file_id": str(file_id)}
        else:
            return {"message": "업로드 성공했으나 분석 요청 실패", "file_id": str(file_id)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/caps")

@app.get("/api/results")
async def get_results(filename: str = None, start_date: str = None):
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM analysis_results WHERE 1=1"
        params = []
        
        if filename:
            query += " AND filename ILIKE %s"
            params.append(f"%{filename}%")
        
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
            
        query += " ORDER BY created_at DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []

@app.get("/api/alerts")
async def get_alerts():
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # 분석 결과에서 알림 목록만 추출
        cur.execute("SELECT analysis_data->'alerts' as alerts FROM analysis_results WHERE analysis_data->'alerts' IS NOT NULL ORDER BY created_at DESC LIMIT 20")
        rows = cur.fetchall()
        alerts = []
        for row in rows:
            if row['alerts']:
                alerts.extend(row['alerts'])
        cur.close()
        conn.close()
        return alerts
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []

@app.get("/api/devices", response_model=List[Device])
async def get_devices():
    locations = ["강남역 1번 출구", "홍대입구역 9번 출구", "광화문 광장", "잠실역 사거리"]
    return [
        Device(
            id=f"DEV-{i:03d}",
            location=random.choice(locations),
            status="활성" if random.random() > 0.2 else "비활성",
            object_count=random.randint(0, 100)
        ) for i in range(1, 6)
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
