"""Job progress & cancellation serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "user",
            "job_type",
            "status",
            "progress_percent",
            "stage_name",
            "metrics",
            "error_message",
            "heartbeat_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at")
