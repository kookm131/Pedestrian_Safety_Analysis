# Cloud Storage Optimization Guide (GCS FUSE)

CAPS 프로젝트에서 대용량 영상 데이터를 효율적으로 처리하기 위해 Google Cloud Storage FUSE를 활용하는 가이드입니다.

## 1. 개요
전용 AI 분석 워크로드를 위해 S3 또는 GCS를 로컬 파일 시스템처럼 마운트하여, 데이터 복사 단계 없이 즉시 분석(In-place processing)을 수행합니다.

## 2. 마운트 설정 (K8s Sidecar 예시)
`backend/worker` 파드에 아래와 같은 리소스 설정을 추가하여 스토리지 성능을 최적화합니다.

```yaml
annotations:
  gke-gcsfuse.sidecar.gke.io/urls: "true"
  gke-gcsfuse.sidecar.gke.io/mount-options: "implicit-dirs,only-dir=videos"
```

## 3. 코드 적용
`worker.py`에서 `os.path.exists()` 등을 통해 마운트된 경로(` /mnt/gcs/videos/`)에 직접 접근하여 영상 처리를 가속화합니다.
```python
# 예시: GridFS 대신 로컬 마운트 경로 사용
if os.path.exists("/mnt/gcs/videos/" + filename):
    cap = cv2.VideoCapture("/mnt/gcs/videos/" + filename)
```

## 4. 기대 효과
- **데이터 로딩 시간 단축**: 대용량 영상 다운로드 불필요 (Streaming read)
- **비용 절감**: 로컬 스토리지 비용 및 데이터 전송 비용 최소화
