"""File metadata JSONB store."""

from __future__ import annotations

import uuid

from django.db import models

from apps.catalog.models import File


class FileMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name="metadata")
    data = models.JSONField(default=dict)
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "catalog_filemetadata"
