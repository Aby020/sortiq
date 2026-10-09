"""Operations serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.operations.models import Operation, OperationItem


class OperationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationItem
        fields = (
            "id",
            "operation",
            "item_index",
            "source_path",
            "target_path",
            "action",
            "status",
            "pre_state",
            "post_state",
            "error_message",
        )
        read_only_fields = (
            "id",
            "operation",
            "item_index",
            "source_path",
            "target_path",
            "action",
            "status",
            "pre_state",
            "post_state",
            "error_message",
        )


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = (
            "id",
            "user",
            "status",
            "total_items",
            "successful_items",
            "failed_items",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "status",
            "total_items",
            "successful_items",
            "failed_items",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
