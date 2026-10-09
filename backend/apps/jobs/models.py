"""Background job tracking."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="jobs",
    )
    job_type = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16,
        choices=[
            ("pending", "pending"),
            ("running", "running"),
            ("completed", "completed"),
            ("failed", "failed"),
            ("cancelled", "cancelled"),
        ],
        default="pending",
    )
    progress_percent = models.IntegerField(default=0)
    stage_name = models.CharField(max_length=128, blank=True)
    metrics = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    heartbeat_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jobs_job"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progress_percent__gte=0)
                & models.Q(progress_percent__lte=100),
                name="job_progress_range",
            ),
        ]
