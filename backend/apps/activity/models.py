"""Audit log / system events."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    event_type = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_activity"
        ordering = ["-created_at"]
