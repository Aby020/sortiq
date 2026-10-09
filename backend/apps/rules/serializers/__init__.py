"""Rules serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.rules.models import OrganizationRule


class OrganizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRule
        fields = (
            "id", "user", "name", "priority", "is_active",
            "conditions", "actions", "created_at", "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at")
