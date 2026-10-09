"""Catalog domain — categories and files."""

from __future__ import annotations

import uuid

from django.db import models

from apps.folders.models import Folder


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=32, blank=True)
    color = models.CharField(max_length=7, blank=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_category"
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.name


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="files")
    relative_path = models.CharField(max_length=1024)
    canonical_path = models.CharField(max_length=1024)
    name = models.CharField(max_length=256)
    extension = models.CharField(max_length=32, blank=True)
    is_directory = models.BooleanField(default=False)
    size_bytes = models.BigIntegerField(default=0)
    mtime_ns = models.BigIntegerField(null=True, blank=True)
    ctime_ns = models.BigIntegerField(null=True, blank=True)
    inode_identity = models.CharField(max_length=64, blank=True)
    is_symlink = models.BooleanField(default=False)
    mime_type = models.CharField(max_length=128, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="files"
    )
    sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    partial_hash = models.CharField(max_length=64, blank=True)
    hash_stage = models.CharField(
        max_length=16,
        choices=[
            ("none", "none"),
            ("partial", "partial"),
            ("full", "full"),
            ("error", "error"),
        ],
        default="none",
    )
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_file"
        indexes = [
            models.Index(fields=["folder", "canonical_path"]),
            models.Index(fields=["extension"]),
            models.Index(fields=["category"]),
            models.Index(fields=["sha256"]),
            models.Index(fields=["deleted_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["folder", "relative_path"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_file_path_active",
            ),
            models.CheckConstraint(
                condition=models.Q(size_bytes__gte=0),
                name="file_size_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return self.name
