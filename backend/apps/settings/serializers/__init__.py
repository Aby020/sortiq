"""Settings serializer."""

from __future__ import annotations

from rest_framework import serializers


class SettingsSerializer(serializers.Serializer):
    max_upload_size = serializers.CharField(max_length=16)
    default_recursive = serializers.BooleanField()
    default_follow_symlinks = serializers.BooleanField()
    hash_stage_default = serializers.CharField(max_length=16)
