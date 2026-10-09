"""Organization suggestions domain."""

from __future__ import annotations

import uuid

from django.db import models

from apps.authentication.models import User
from apps.catalog.models import File
from apps.rules.models import OrganizationRule


class OrganizationSuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suggestions")
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name="suggestions"
    )
    rule = models.ForeignKey(
        OrganizationRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suggestions",
    )
    proposed_action = models.JSONField(default=dict)
    confidence = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=16,
        choices=[
            ("pending", "pending"),
            ("accepted", "accepted"),
            ("dismissed", "dismissed"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suggestions_organization_suggestion"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(confidence__gte=0.0)
                & models.Q(confidence__lte=1.0),
                name="suggestion_confidence_range",
            ),
        ]
