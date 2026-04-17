from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import datetime
import random
import os
import json
from database import init_postgres, fs, publish_task, SessionLocal, AnalysisResult, cache_get, cache_set

app = FastAPI(title="CAPS Backend API")

# DB 초기화
init_postgres()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/api/status", "/docs", "/openapi.json"]:
        return await call_next(request)
    auth_header = request.headers.get("Authorization")
    if not auth_header and os.getenv("STRICT_AUTH", "false") == "true":
         raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

class Device(BaseModel):
    id: str
    location: str
    status: str
    object_count: int

@app.get("/api/status")
async def get_status():
    cache_key = "system_status"
    cached_status = cache_get(cache_key)
    if cached_status:
        return cached_status
    
    status = {"status": "정상", "timestamp": datetime.datetime.now().isoformat()}
    cache_set(cache_key, status, expire=60) # 1분 캐시
    return status

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # 1. MongoDB GridFS에 저장 (database.py의 fs 사용)
        file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
        
        # 2. 업로드 내역 정보 구성
        upload_info = {
            "file_id": str(file_id),
            "filename": file.filename,
            "upload_at": datetime.datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # 3. RabbitMQ 메시지 발행 (database.py의 publish_task 사용)
        if publish_task(upload_info):
            return {"message": "업로드 성공 및 분석 요청 완료", "file_id": str(file_id)}
        else:
            return {"message": "업로드 성공했으나 분석 요청 실패", "file_id": str(file_id)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results")
async def get_results(filename: str = None, start_date: str = None):
    # 필터가 없을 때만 캐시 적용
    cache_key = "all_results_latest"
    if not filename and not start_date:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data

    try:
        db = SessionLocal()
        query = db.query(AnalysisResult)
        
        if filename:
            query = query.filter(AnalysisResult.filename.ilike(f"%{filename}%"))
        
        if start_date:
            try:
                dt = datetime.datetime.fromisoformat(start_date)
                query = query.filter(AnalysisResult.created_at >= dt)
            except:
                pass
                
        results = query.order_by(AnalysisResult.created_at.desc()).limit(50).all()
        db.close()
        
        data = [
            {
                "id": r.id,
                "file_id": r.file_id,
                "filename": r.filename,
                "analysis_data": r.analysis_data,
                "processed_file_id": r.processed_file_id,
                "created_at": r.created_at.isoformat()
            } for r in results
        ]
        
        # 필터 없을 때 캐시 저장
        if not filename and not start_date:
            cache_set(cache_key, data, expire=120) # 2분 캐시
            
        return data
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []

@app.get("/api/alerts")
async def get_alerts():
    try:
        db = SessionLocal()
        # JSON 컬럼 내의 alerts 추출 (PostgreSQL 기능 활용)
        results = db.query(AnalysisResult).filter(AnalysisResult.analysis_data['alerts'].isnot(None)).order_by(AnalysisResult.created_at.desc()).limit(20).all()
        alerts = []
        for r in results:
            if r.analysis_data and 'alerts' in r.analysis_data:
                alerts.extend(r.analysis_data['alerts'])
        db.close()
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
