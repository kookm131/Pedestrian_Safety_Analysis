# 프로젝트 구현 계획: 보행자 안전 분석 플랫폼 (CAPS)

Flask, Redis, RabbitMQ, Flink 및 React를 사용하여 이벤트 기반 아키텍처(EDA) 기반의 실시간 보행자 안전 분석 플랫폼을 구현합니다. **모든 사용자 인터페이스(UI)와 시스템 텍스트는 한국어로 구현됩니다.**

## Proposed Changes

### Infrastructure (Docker)

#### [NEW] [docker-compose.yml](file:///c:/work/tech/docker-compose.yml) 
- Define services for `flask-backend`, `react-frontend`, `redis`, `rabbitmq`, and `flink-jobmanager`/`flink-taskmanager`.
- Set up networks and volumes for persistent data.

---

### Backend (Flask)

#### [NEW] [flask-backend/Dockerfile](file:///c:/work/tech/flask-backend/Dockerfile)
- Python 3.10 based container with necessary dependencies (flask, redis, pika, flask-cors).

#### [NEW] [flask-backend/app.py](file:///c:/work/tech/flask-backend/app.py)
- Main entry point for the Flask API.
- Endpoints for retrieving device status, historical logs, and real-time alerts.

---

### Stream Processing (Flink)

#### [NEW] [flink-processor/job.py](file:///c:/work/tech/flink-processor/job.py)
- PyFlink job to consume detection logs from RabbitMQ, perform windowed aggregations (e.g., density scoring), and produce results back to an alert queue.

---

### Frontend (React)

#### [MODIFY] [frontend/package.json](file:///c:/work/tech/frontend/package.json)
- Add dependencies: `d3`, `plotly.js-dist-min`, `axios`, `tailwindcss`, `postcss`, `autoprefixer`.

#### [NEW] [frontend/src/components/Dashboard.tsx](file:///c:/work/tech/frontend/src/components/Dashboard.tsx)
- Main dashboard layout using Tailwind CSS with a premium dark-mode aesthetic.

#### [NEW] [frontend/src/components/DensityHeatmap.tsx](file:///c:/work/tech/frontend/src/components/DensityHeatmap.tsx)
- Visualization component using D3.js to display pedestrian density.

#### [NEW] [frontend/src/components/ObjectChart.tsx](file:///c:/work/tech/frontend/src/components/ObjectChart.tsx)
- Real-time chart using Plotly to show object detection trends.

## Verification Plan

### Automated Tests
- Integration test for message flow: Producer (Backend) -> RabbitMQ -> Flink -> Alert Queue -> Backend -> Frontend.

### Manual Verification
- Verify the Docker-compose setup starts all services correctly.
- Open the dashboard at `http://localhost:5173` and check real-time data visualization.
- Simulate detection log inputs and verify the density heatmap and charts update accordingly.
