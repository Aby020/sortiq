"""Organization rules domain."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User


class OrganizationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=256)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rules_organizationrule"
        ordering = ["-priority", "name"]
