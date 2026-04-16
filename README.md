# CAPS: Cloud-AI Pedestrian Safety Analysis Platform

이 프로젝트는 최신 SOTA AI를 활용한 보행자 안전 분석 플랫폼의 전체 스택 구현체입니다.

## 시스템 구성
- **Frontend**: React, D3, Plotly (Vite 기반)
- **Backend**: FastAPI (Python)
- **Data Services**:
  - PostgreSQL (장치/사용자 데이터)
  - MongoDB (탐지 로그)
  - Redis (실시간 캐시)
  - RabbitMQ (이벤트 메시징)
  - Flink (실시간 스트림 처리)

## 실행 방법

### 사전 요구 사항
- Docker 및 Docker Compose

### 서비스 시작
루트 디렉토리에서 아래 명령어를 실행하세요:

```bash
docker-compose up --build
```

### 접속 정보
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:5000](http://localhost:5000)
- **RabbitMQ 관리 UI**: [http://localhost:15672](http://localhost:15672) (guest/guest)
- **Flink Dashboard**: [http://localhost:8081](http://localhost:8081)

## 상세 정보
- [Backend 구현](file:///c:/work/tech1/backend/main.py)
- [Docker 설정](file:///c:/work/tech1/docker-compose.yml)
- [요구사항 정의(PRD)](file:///c:/work/tech1/docu/prd_1.md)
