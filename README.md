# CAPS: Cloud-AI Pedestrian Safety Analysis Platform

이 프로젝트는 최신 SOTA AI를 활용한 보행자 안전 분석 및 통합 관제 플랫폼입니다.

## 🌟 프로젝트 개요
**CAPS (Cloud-AI Pedestrian Safety Analysis Platform)**는 최신 객체 탐지 알고리즘(YOLOv11 등)과 클라우드 네이티브 인프라를 결합하여 복잡한 도심 환경에서 보행자 안전을 실시간으로 분석하고 다중 밀집 사고를 예방하는 솔루션입니다.

## 🚀 핵심 기능
- **AI 영상 분석 엔진**: YOLOv7, v10, v11, v26 등 최신 알고리즘을 통한 실시간 객체 식별 및 인파 밀집도 분석
- **실시간 위험 탐지**: 무단횡단, 특정 구역 과밀집 등 정의된 위험 시나리오 자동 감지 및 알림
- **개인정보 보호**: 탐지된 안면 및 차량 번호판 실시간 가명 처리 (Blur/Masking)
- **통합 모니터링 대시보드**: 객체별 통계, 서버 상태, 오토스케일링 현황 시각화
- **이벤트 기반 확장성**: RabbitMQ와 KEDA를 활용한 트래픽 기반 GPU 자원 자동 확장 (Autoscaling)

## 🛠 시스템 구성 및 기술 스택
- **Frontend**: React, Vite, D3.js, Plotly, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Inference**: NVIDIA TensorRT, Managed AI Services (SageMaker/Vertex AI)
- **Data & Messaging**:
  - **PostgreSQL**: 장치 및 마스터 데이터 관리
  - **MongoDB**: AI 탐지 로그 데이터 저장
  - **Redis**: 실시간 데이터 캐싱
  - **RabbitMQ**: 비동기 이벤트 메시징 및 버퍼링
  - **Flink**: 실시간 데이터 스트림 처리
- **Infrastructure**: Docker, Kubernetes, KEDA, GCS FUSE

## 📁 프로젝트 구조
```text
.
├── backend/            # FastAPI 기반 API 서버
├── frontend/           # React 기반 대시보드 웹 서비스
├── docu/               # 프로젝트 정의서, 계획서 및 설계 문서
├── docker-compose.yml  # 로컬 개발 환경 구성
└── README.md           # 프로젝트 개요 및 실행 가이드
```

## 📋 상세 상세정보 및 문서
프로젝트의 상세한 설계와 추진 계획은 아래 문서들을 참고해 주세요.

- [**요구사항 정의 (PRD)**](docu/prd_1.md): 프로젝트 목표, 주요 기능 및 기술 요구사항
- [**수행 계획서 (Plan)**](docu/plan.md): 단계별 일정, 산출물 및 품질 관리 전략
- [**화면 설계서 (UI Design)**](docu/ui_design_1.md): 대시보드 및 모바일 UI 구성 설명
- [**구현 계획 (Implementation)**](docu/implementation_plan.md): 아키텍처 및 상세 구현 로드맵

## ⚙️ 실행 방법

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
