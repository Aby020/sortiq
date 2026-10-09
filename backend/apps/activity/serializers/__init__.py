"""Activity serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.activity.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "user", "event_type", "description", "metadata", "created_at")
        read_only_fields = ("id", "user", "created_at")
