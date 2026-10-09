"""Duplicate group and membership."""

from __future__ import annotations

import uuid

from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import File


class DuplicateGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size_bytes = models.BigIntegerField(validators=[MinValueValidator(0)])
    sha256 = models.CharField(max_length=64, unique=True, db_index=True)
    member_count = models.IntegerField(default=0)
    reclaimable_bytes = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "duplicates_duplicategroup"

    def __str__(self) -> str:
        return f"{self.sha256[:16]}..."


class DuplicateMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        DuplicateGroup, on_delete=models.CASCADE, related_name="members"
    )
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="duplicate_memberships")
    is_keeper = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "duplicates_duplicatemember"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "file"],
                name="unique_group_file_member",
            ),
        ]
