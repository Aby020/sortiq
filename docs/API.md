# API Contract

Public REST: `/api/v1/auth/`, `/folders/`, `/files/`, `/categories/`, `/duplicates/`, `/rules/`, `/suggestions/`, `/operations/`, `/jobs/`, `/activity/`. Internal FastAPI: `GET /internal/scan-stream`, `POST /internal/hash-batch`. All endpoints use standard DRF pagination/filtering; error envelope is `{"error": {"code", "message", "details", "request_id", "status"}}`.
