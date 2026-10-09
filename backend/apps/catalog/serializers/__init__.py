"""Catalog serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import Category, File
from apps.catalog.models_metadata import FileMetadata


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "slug", "name", "description", "icon", "color", "is_system")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id", "folder", "relative_path", "canonical_path", "name",
            "extension", "is_directory", "size_bytes", "mime_type",
            "category", "sha256", "hash_stage", "first_seen_at",
            "last_seen_at", "deleted_at",
        )
        read_only_fields = (
            "id", "folder", "relative_path", "canonical_path", "name",
            "extension", "is_directory", "size_bytes", "mime_type",
            "category", "sha256", "hash_stage", "first_seen_at",
            "last_seen_at", "deleted_at",
        )


class FileMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileMetadata
        fields = ("id", "file", "data", "extracted_at")
        read_only_fields = ("id", "file", "data", "extracted_at")
