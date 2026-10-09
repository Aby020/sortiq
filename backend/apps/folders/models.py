"""Folder domain model."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="folders")
    path = models.CharField(max_length=1024)
    name = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)
    is_watched = models.BooleanField(default=False)
    recursive = models.BooleanField(default=True)
    follow_symlinks = models.BooleanField(default=False)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "folders_folder"
        indexes = [
            models.Index(fields=["user", "path"]),
            models.Index(fields=["is_active", "is_watched"]),
        ]

    def __str__(self) -> str:
        return self.name
