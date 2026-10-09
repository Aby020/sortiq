"""Native background job maintenance (replaces Celery beat)."""

from __future__ import annotations

from apps.catalog.tasks import maintenance


def maintenance_job() -> dict:
    """Queue scans for stale folders; dispatched on the FastAPI thread pool."""

    return maintenance()
