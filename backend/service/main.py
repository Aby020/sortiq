"""FastAPI execution plane for the Sortiq control plane."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

logger = structlog.get_logger(__name__)

INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN", "local-desktop")


def _setup_django() -> None:
    """Configure Django ORM lazily so the execution plane can persist jobs."""

    import sys

    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    import django

    django.setup()

app = FastAPI(
    title="Sortiq Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8100",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8100",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_service_token(request: Request) -> None:
    token = request.headers.get("X-Internal-Service-Token")
    if not token or token != INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "auth_failed",
                    "message": "Invalid or missing X-Internal-Service-Token.",
                    "details": {},
                    "request_id": request.headers.get("X-Request-ID", "unknown"),
                    "status": HTTP_401_UNAUTHORIZED,
                }
            },
        )


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "sortiq-fastapi",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/internal/scan-job")
def internal_scan_job(
    folder_id: str,
    job_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    _auth: None = Depends(require_service_token),
) -> dict:
    """Dispatch a native background scan; replaces Celery shared_task."""

    _setup_django()
    from apps.catalog.tasks import dispatch_scan  # noqa: E402

    background_tasks.add_task(dispatch_scan, folder_id, job_id)
    return {
        "status": "queued",
        "folder_id": folder_id,
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/internal/health")
def internal_health(request: Request, _auth: None = Depends(require_service_token)) -> dict:  # noqa: ARG001
    return {
        "status": "ok",
        "uptime": "running",
        "pid": os.getpid(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "sortiq-fastapi-v2",
        "version": "0.2.0",
    }
