[PRD] 클라우드 기반 보행영상 AI 분석 플랫폼 - 제1단계: 요구사항 정의
1. 프로젝트 개요
제품명: Cloud-AI Pedestrian Safety Analysis Platform (CAPS)
핵심 가치: 최신 SOTA(YOLOv11 등) AI를 활용하여 복잡한 도심 환경에서 보행자 및 객체를 실시간으로 탐지하고, 클라우드 인프라를 통해 확장성과 안정성을 확보하여 다중 밀집 사고를 예방함
.
2. 기능 요소 (Functional Requirements)
가. AI 영상 분석 엔진
객체 탐지 및 분류: YOLOv7, v10, v11, v26 등 최신 알고리즘을 활용하여 보행자, 동물, 차량, 교통 표지판을 실시간으로 식별함
.
밀집도 분석: 어텐션 메커니즘(Attention Mechanism)을 적용하여 인파가 겹치거나 가려진 환경에서도 정확한 보행자 수를 카운팅하고 밀집도를 계산함
.
위험 상황 감지: 무단횡단, 특정 구역 인파 밀집, 동물 진입 등 정의된 위험 시나리오 발생 시 이벤트를 생성함
.
영상 가명 처리: 개인정보 보호를 위해 탐지된 보행자의 안면 및 차량 번호판을 실시간으로 모너니트링 화면과 저장 데이터에서 블러(Blur) 또는 마스킹 처리함
.
나. 데이터 및 관리 시스템
실시간 스트리밍 및 재생: 클라우드 서버를 통해 수집된 영상을 실시간으로 송출하고, 과거 분석 이력을 조회 및 재생함
.
통합 대시보드: 객체별 통계, 서버 상태, 오토스케일링 현황, 위험 알림을 시각화하여 제공함
.
전용 모니터링 App: 관리자가 모바일 기기에서 실시간 알림 푸시를 받고 현장 상황을 확인할 수 있는 기능을 제공함
.
3. 비기능 요소 (Non-Functional Requirements)
가. 성능 및 확장성 (Performance & Scalability)
추론 최적화: NVIDIA TensorRT 엔진을 적용하여 FP16/INT8 정밀도 기반의 초고속 추론(Latency 최소화)을 달성함
.
지능형 오토스케일링: Kubernetes 환경에서 KEDA를 도입하여 실제 트래픽(메시지 큐 대기 수 등)에 따라 GPU 자원을 유동적으로 확장/축소하여 자원 효율성을 극대화함
.
데이터 처리 효율: GCS FUSE 등을 활용하여 대규모 데이터셋에 대한 액세스 속도를 높이고 스토리지 비용을 절감함
.
나. 안정성 및 보안 (Reliability & Security)
고가용성(HA): 클라우드 기반 관리형 서비스(Amazon SageMaker 또는 Google Vertex AI)를 활용하여 시스템 중단 없는 24/7 서비스 체계를 구축함
.
법적 준수: 개인정보보호법 및 가명정보 처리 가이드라인을 철저히 준수하여 비식별화 품질을 유지함
.
보안 아키텍처: 제로 트러스트(Zero Trust) 보안 모델을 검토하여 데이터 접근 권한을 엄격히 관리함
.
다. 운영 및 품질 (Operations & Quality)
SOTA 모델 벤치마킹: 최소 5종 이상의 최신 AI 모델 성능을 비교 검증하여 최적의 솔루션을 유지함
.
통합 테스트: AI 모델의 정확도(mAP), 초당 프레임 수(FPS), 서버 부하 테스트를 포함한 통합 테스트 명세서를 작성하고 검증함
.

[PRD] 클라우드 기반 보행영상 AI 분석 플랫폼 - 제2단계: 기술 설계
4. 시스템 아키텍처 (System Architecture)
본 시스템은 고가용성과 실시간 처리를 위해 **이벤트 기반 마이크로서비스 아키텍처(EDA)**를 채택합니다.
Ingestion Layer (영상 수집):
도심 교차로 CCTV 및 이동형 장치(로봇, 드론)로부터 영상 스트림 수집
.
Privacy Proxy: 클라우드 전송 전 단계에서 엣지 단의 가명처리(안면/번호판 모자이크)를 수행하여 개인정보 유출 방지
.
Storage & Messaging Layer:
Data Lake: 원본 및 처리 영상 저장을 위한 S3/GCS 활용. GCS FUSE를 사용하여 데이터 접근 속도 최적화
.
Message Broker (RabbitMQ): 영상 분석 요청을 비동기 큐로 관리하여 트래픽 급증 시 버퍼 역할 수행
.
AI Inference Layer (Cloud Native AI):
Managed Service: Amazon SageMaker 또는 Google Vertex AI 상에 YOLOv11/v26 모델 배포
.
Optimization: NVIDIA TensorRT를 적용하여 FP16 정밀도로 추론 성능 극대화
.
Autoscaling: Kubernetes 환경에서 KEDA를 사용해 큐에 쌓인 메시지 수에 따라 GPU 파드(Pod)를 유동적으로 오토스케일링
.
Application & Serving Layer:
Backend API: 분석 결과를 가공하여 DB에 저장하고 프론트엔드에 전달.
Client Interface: 실시간 모니터링 웹 대시보드 및 관리자용 모바일 App
.
5. 메시지 구조 (Message Structure)
AI 분석 결과 및 이벤트 전달을 위한 표준 JSON 메시지 규격입니다.
Detection Result Message (JSON 예시):
6. 데이터베이스 ERD (Entity Relationship Diagram) 설계
관계형 DB를 통해 데이터 간 정합성을 유지하며, 대규모 로그 처리를 위해 시계열적 관리를 수행합니다.
주요 엔티티(Entity) 구성:
Device (장치): device_id(PK), location, status, ip_address, last_heartbeat
Video_Stream (영상): video_id(PK), device_id(FK), start_time, end_time, storage_path
Detection_Log (탐지 이력): log_id(PK), video_id(FK), timestamp, object_count, density_score
Detected_Object (탐지 객체 상세): obj_id(PK), log_id(FK), class_type, confidence, bbox_data
Alert_Event (위험 알림): event_id(PK), log_id(FK), event_type(무단횡단/밀집/사고), is_confirmed
User (사용자): user_id(PK), username, role(관리자/관제원), auth_token
관계 설정:
Device : Video_Stream = 1 : N
Video_Stream : Detection_Log = 1 : N
Detection_Log : Detected_Object = 1 : N (프레임당 여러 객체 탐지)
Detection_Log : Alert_Event = 1 : 1 (특정 탐지 상황이 이벤트를 트리거)

[PRD] 클라우드 기반 보행영상 AI 분석 플랫폼 - 제3단계: 구현 및 배포 전략
7. 상세 구현 전략 (Implementation Strategy)
가. AI 모델 최적화 및 가명처리 구현
엔진 최적화: 최신 YOLOv11 또는 YOLOv26 모델을 선정하고, NVIDIA TensorRT를 활용하여 FP16/INT8 정밀도 교정을 수행함으로써 실시간 성능을 극대화합니다
.
실시간 비식별화: 영상 데이터 수집 즉시 보행자의 안면과 차량 번호판을 탐지하여 모자이크 또는 블러 처리하는 가명처리 로직을 최우선으로 적용합니다
.
데이터 핸들링: 대규모 데이터셋의 효율적 관리를 위해 GCS FUSE를 활용하여 로컬 파일 시스템처럼 클라우드 스토리지에 고속으로 접근합니다
.
나. 클라우드 인프라 및 오토스케일링 고도화
서빙 인프라: Amazon SageMaker Endpoints 또는 Google Vertex AI와 같은 관리형 서비스를 활용하여 가용성 높은 모델 추론 환경을 구축합니다
.
이벤트 기반 스케일링: KEDA를 도입하여 RabbitMQ 큐에 쌓인 미처리 영상 수에 따라 GPU 파드(Pod)를 자동으로 확장/축소하여 자원 낭비를 최소화합니다
.
백엔드/프론트엔드: 분석 결과를 실시간으로 송출하기 위한 Web/App 통합 모니터링 시스템을 구현합니다
.
8. 테스트 및 품질 관리 (Testing & QA)
AI 성능 검증: mAP(mean Average Precision) 89% 이상 확보 및 FPS(Frames Per Second) 77 이상의 실시간성 보장을 목표로 테스트를 수행합니다
.
통합 테스트: 영상 수집 장치부터 클라우드 분석, 최종 대시보드 출력까지의 전 과정(End-to-End) 연동을 검증합니다
.
부하 테스트: 트래픽 급증 시 오토스케일링이 지연 없이 작동하는지 확인하고, TensorRT 엔진 적용 전후의 추론 속도 개선 수치(최대 4배 절감 기대)를 측정합니다
.
보안 점검: 개인정보보호 가이드라인에 따른 가명처리 품질을 검수하고, 외부 접속 차단(제로 트러스트 모델) 상태에서의 데이터 안정성을 확인합니다
.
9. 배포 및 운영 계획 (Deployment & Operations)
지속적 통합/배포(CI/CD): 모델 학습 완료 후 자동으로 커스텀 예측 컨테이너를 빌드하여 Artifact Registry에 등록하고 무중단 배포를 수행합니다
.
실시간 모니터링: Amazon CloudWatch 또는 커스텀 대시보드를 통해 서버 부하, 에러 로그, GPU 사용률을 실시간으로 추적하고 이상 발생 시 관리자 앱으로 푸시 알림을 발송합니다
.
유지보수: SOTA AI 알고리즘 업데이트 주기에 맞춰 최소 5종 이상의 최신 모델 성능을 지속적으로 벤치마킹하여 플랫폼 경쟁력을 유지합니다
.