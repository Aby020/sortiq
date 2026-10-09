"""Celery periodic maintenance & auto-scan beat tasks."""

from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from apps.folders.models import Folder
from apps.jobs.models import Job


@shared_task(bind=True)
def maintenance_task(self) -> dict:
    stale = Folder.objects.filter(
        last_scanned_at__lt=timezone.now() - __import__("datetime").timedelta(days=7),
        is_active=True,
    )
    queued = 0
    for folder in stale[:10]:
        Job.objects.create(
            user=folder.user,
            job_type="scan",
            status="pending",
            stage_name="queued_by_beat",
        )
        queued += 1
    return {"stale_folders": stale.count(), "queued": queued}
