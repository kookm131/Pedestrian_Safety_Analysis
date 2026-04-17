import json
import os
import pika
from database import RABBITMQ_URL, redis_client

# PyFlink가 설치되어 있다는 가정하의 스켈레톤 코드입니다.
# 실제 운영 환경에서는 Flink Cluster에 제출(submit)되어 실행됩니다.

def process_stream():
    """
    RabbitMQ로부터 실시간 탐지 이벤트를 소비하여 
    이동 평균(Moving Average) 또는 복합 위험 지수를 계산하는 시뮬레이션
    """
    print("[*] Flink Stream Processor Skeleton Starting...")
    
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    # 분석 완료 이벤트를 받을 별도의 큐가 있다고 가정 (또는 분석 워커와 공유)
    channel.queue_declare(queue='analysis_events', durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [Flink] Received data for complex analysis: {data['filename']}")
        
        # 1. 윈도우 기반 분석 시뮬레이션 (최근 5개 분석의 평균 밀집도)
        risk_score = data.get('risk_score', 0)
        
        # Redis를 상태 저장소(State Store)로 활용하여 이동 평균 계산
        window_key = "flink_sliding_window_risk"
        current_window = redis_client.lrange(window_key, 0, 4)
        current_window = [float(x) for x in current_window]
        current_window.append(risk_score)
        
        if len(current_window) > 5:
            current_window.pop(0)
            
        # 새로운 윈도우 저장
        redis_client.delete(window_key)
        if current_window:
            redis_client.rpush(window_key, *current_window)
            
        avg_risk = sum(current_window) / len(current_window)
        print(f" [Flink] Rolling Average Risk Score: {avg_risk:.2f}")
        
        # 2. 복합 이벤트 처리 (CEP) 시뮬레이션
        if avg_risk > 0.8:
            print(" [Flink] ALERT: Sustained high density detected!")
            redis_client.set("global_danger_level", "HIGH", ex=60)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='analysis_events', on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    # 실제로는 PyFlink의 StreamExecutionEnvironment를 통해 실행됩니다.
    # 여기서는 로직 흐름을 보여주기 위한 시뮬레이션 모드로 작동합니다.
    try:
        process_stream()
    except KeyboardInterrupt:
        print("Stopping Flink Processor...")
