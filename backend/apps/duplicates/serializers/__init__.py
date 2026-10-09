"""Duplicate serializers."""

from __future__ import annotations

from rest_framework import serializers

from apps.duplicates.models import DuplicateGroup, DuplicateMember


class DuplicateMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DuplicateMember
        fields = ("id", "file", "is_keeper")


class DuplicateGroupSerializer(serializers.ModelSerializer):
    members = DuplicateMemberSerializer(many=True, read_only=True)

    class Meta:
        model = DuplicateGroup
        fields = (
            "id", "size_bytes", "sha256", "member_count",
            "reclaimable_bytes", "members", "created_at", "updated_at",
        )
        read_only_fields = ("members",)
