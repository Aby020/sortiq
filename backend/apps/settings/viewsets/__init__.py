"""User settings API."""

from __future__ import annotations

from apps.settings.serializers import SettingsSerializer
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response


class SettingsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SettingsSerializer

    def get(self, request: Request) -> Response:
        data = {
            "max_upload_size": "100MB",
            "default_recursive": True,
            "default_follow_symlinks": False,
            "hash_stage_default": "none",
        }
        return Response(data)

    def patch(self, request: Request) -> Response:
        return Response({"status": "updated"})
