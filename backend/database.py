import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from pymongo import MongoClient
import gridfs
import pika
import json

import redis
import json

# --- 환경 변수 관리 ---
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/caps")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/caps")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# --- Redis 설정 ---
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def cache_set(key: str, value: any, expire: int = 300):
    try:
        redis_client.set(key, json.dumps(value), ex=expire)
    except Exception as e:
        print(f"Redis Set Error: {e}")

def cache_get(key: str):
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Redis Get Error: {e}")
        return None

# --- PostgreSQL (SQLAlchemy) 설정 ---
Base = declarative_base()
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    analysis_data = Column(JSON)
    processed_file_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_postgres():
    Base.metadata.create_all(bind=engine)

# --- MongoDB 설정 ---
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client.get_database()
fs = gridfs.GridFS(mongo_db)

# --- RabbitMQ 설정 ---
def get_rabbitmq_channel():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='video_analysis_task', durable=True)
    return connection, channel

def publish_task(message: dict):
    try:
        connection, channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange='',
            routing_key='video_analysis_task',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"RMQ Publish Error: {e}")
        return False
