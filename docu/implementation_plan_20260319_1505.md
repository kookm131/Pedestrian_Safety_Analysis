# Implementation Plan - Video Analysis Pipeline

Implement a full pipeline for uploading, storing, analyzing, and viewing video analysis results using YOLO v11.

## Proposed Changes

### [Backend](file:///c:/work/tech1/backend)

#### [MODIFY] [requirements.txt](file:///c:/work/tech1/backend/requirements.txt)
- Add `pymongo` and `ultralytics` (for YOLO v11).
- Add `python-multipart` (for file uploads in FastAPI).

#### [MODIFY] [main.py](file:///c:/work/tech1/backend/main.py)
- Add `/api/upload` endpoint using `UploadFile`.
- Implement MongoDB GridFS storage logic.
- Implement RabbitMQ producer to send message after upload.
- Add `/api/results` endpoint to fetch analysis results from PostgreSQL.

#### [NEW] [worker.py](file:///c:/work/tech1/backend/worker.py)
- Implement RabbitMQ consumer.
- Load YOLO v11 model and analyze video.
- Save results to PostgreSQL.
- Handle "analysis complete" messaging if needed.

### [Frontend](file:///c:/work/tech1/frontend)

#### [MODIFY] [src/App.tsx](file:///c:/work/tech1/frontend/src/App.tsx)
- Add a video upload section.
- Add a results list/dashboard.

#### [NEW] [src/components/VideoUpload.tsx](file:///c:/work/tech1/frontend/src/components/VideoUpload.tsx)
- Component for handling file selection and upload progress.

#### [NEW] [src/components/AnalysisResults.tsx](file:///c:/work/tech1/frontend/src/components/AnalysisResults.tsx)
- Component to display the list of analyzed videos and their results.

## Verification Plan

### Automated Tests
- Upload a sample video file via `curl` to `/api/upload`.
- Check MongoDB GFS for the file.
- Check RabbitMQ for the message.
- Verify worker logs for YOLO analysis.
- Check PostgreSQL for the final results.

### Manual Verification
- Use the web UI to upload a video.
- Observe the results appearing in the dashboard.
