"""Internal FastAPI execution endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, Request

from .main import app, require_service_token


@app.get("/internal/scan-stream")
def internal_scan_stream(request: Request, _: None = Depends(require_service_token)) -> dict:
    return {
        "status": "streaming",
        "folder_id": request.headers.get("X-Folder-ID"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/internal/hash-batch")
def internal_hash_batch(request: Request, _: None = Depends(require_service_token)) -> dict:
    return {
        "status": "hashed_batch",
        "count": len(request.body or b""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
