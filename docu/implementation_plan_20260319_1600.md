# Implementation Plan - Fix MongoDB Port Mismatch

## Problem
The `backend` service in [docker-compose.yml](file:///c:/work/tech1/docker-compose.yml) is configured with an incorrect MongoDB port (`27117`), while the MongoDB container (`db_mongo`) and the `worker` service use the standard port (`27017`). This causes a connection failure when the backend attempts to save videos to GridFS.

## Proposed Changes

### [Docker Compose](file:///c:/work/tech1/docker-compose.yml)

#### [MODIFY] [docker-compose.yml](file:///c:/work/tech1/docker-compose.yml)
- Change `MONGO_URL=mongodb://db_mongo:27117/caps` to `MONGO_URL=mongodb://db_mongo:27017/caps`.

## Verification Plan

### Automated Tests
- `docker compose up -d`: Restart the services with the corrected configuration.
- `echo "test" > test.txt; curl.exe -X POST -F "file=@test.txt" http://localhost:5000/api/upload`: Verify that the upload now returns a 200 OK response.
- `docker compose logs backend`: Verify no 500 errors or connection timeouts in the logs.

### Manual Verification
- Test video upload from the web UI and verify the "업로드 성공" message.
