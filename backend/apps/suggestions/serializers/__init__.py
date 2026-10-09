"""Suggestions serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.suggestions.models import OrganizationSuggestion


class OrganizationSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSuggestion
        fields = (
            "id", "user", "file", "rule", "proposed_action",
            "confidence", "status", "created_at", "updated_at",
        )
        read_only_fields = ("user", "created_at", "updated_at")
