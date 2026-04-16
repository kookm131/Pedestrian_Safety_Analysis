# CAPS Platform Implementation Plan

Implement a full-stack pedestrian safety analysis platform using Docker-compose, featuring a FastAPI backend and various data services.

## Proposed Changes

### [Backend] (New Directory)
- **FastAPI Application**: Create a Python-based API to handle device management, status updates, and data fetching from PostgreSQL/MongoDB.
- **Data Models**: Implement SQLALchemy for PostgreSQL and Motor for MongoDB.
- **Service Integration**: Add clients for Redis (caching) and RabbitMQ (messaging).

### [Infrastructure]
- **docker-compose.yml**: Orchestrate all services:
    - `backend` (FastAPI)
    - `frontend` (React/Vite)
    - `postgres`: Device and user data.
    - `mongodb`: High-frequency detection logs.
    - `redis`: Real-time status/cache.
    - `rabbitmq`: AI analysis event queue.
    - `flink-jobmanager`/`taskmanager`: Stream processing (placeholder/skeletal).

### [Frontend]
- **[App.tsx](file:///c:/work/tech1/frontend/src/App.tsx)**: Update API base URL to point to the backend service in the Docker network.

## Verification Plan
### Automated Tests
- Run `pytest` for backend API endpoints.
- Verify container health using `docker-compose ps`.
### Manual Verification
- Access the dashboard via browser.
- Verify real-time updates and chart rendering with mock data from the backend.
