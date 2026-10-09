"""Folder API serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.folders.models import Folder


class FolderSerializer(serializers.ModelSerializer):
    file_count = serializers.SerializerMethodField()
    total_bytes = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = (
            "id",
            "user",
            "path",
            "name",
            "is_active",
            "is_watched",
            "recursive",
            "follow_symlinks",
            "last_scanned_at",
            "file_count",
            "total_bytes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at", "last_scanned_at")

    def get_file_count(self, obj: Folder) -> int:
        if not hasattr(obj, "_file_count"):
            return obj.files.filter(deleted_at__isnull=True).count()
        return obj._file_count

    def get_total_bytes(self, obj: Folder) -> int:
        if not hasattr(obj, "_total_bytes"):
            return 0
        return obj._total_bytes


class FolderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ("path", "name", "recursive", "follow_symlinks")

    def validate_path(self, value: str) -> str:
        from sortiq_fs.pathguard import validate

        result = validate(value, value)
        if not result.ok:
            raise serializers.ValidationError(result.reason)
        return result.resolved

    def create(self, validated_data: dict) -> Folder:
        user = self.context["request"].user
        return Folder.objects.create(user=user, **validated_data)


class FolderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ("is_active", "is_watched", "recursive", "follow_symlinks")
