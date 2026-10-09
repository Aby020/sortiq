"""Operations and item journals."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User


class Operation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="operations")
    status = models.CharField(
        max_length=24,
        choices=[
            ("planned", "planned"),
            ("executing", "executing"),
            ("completed", "completed"),
            ("partially_completed", "partially_completed"),
            ("failed", "failed"),
            ("cancelled", "cancelled"),
            ("rolled_back", "rolled_back"),
        ],
        default="planned",
    )
    total_items = models.IntegerField(default=0)
    successful_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "operations_operation"


class OperationItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name="items")
    item_index = models.IntegerField()
    source_path = models.CharField(max_length=1024)
    target_path = models.CharField(max_length=1024)
    action = models.CharField(
        max_length=16,
        choices=[
            ("move", "move"),
            ("copy", "copy"),
            ("quarantine", "quarantine"),
            ("delete", "delete"),
        ],
        default="move",
    )
    status = models.CharField(
        max_length=16,
        choices=[
            ("pending", "pending"),
            ("success", "success"),
            ("failed", "failed"),
            ("skipped", "skipped"),
            ("conflict", "conflict"),
        ],
        default="pending",
    )
    pre_state = models.JSONField(default=dict)
    post_state = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "operations_operationitem"
        ordering = ["item_index"]
