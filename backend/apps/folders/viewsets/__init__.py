"""Folder API viewsets."""

from __future__ import annotations

import uuid

from django.db.models import Count, Q, Sum
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.folders.models import Folder
from apps.folders.serializers import (
    FolderCreateSerializer,
    FolderSerializer,
    FolderUpdateSerializer,
)


class FolderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = FolderSerializer

    def get_queryset(self):
        from apps.core.services.desktop_scope import user_scope
        qs = user_scope(self.request, Folder.objects.all(), 'user')
        return qs.annotate(
            _file_count=Count('files', filter=Q(files__deleted_at__isnull=True)),
            _total_bytes=Sum('files__size_bytes'),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return FolderCreateSerializer
        if self.action in ("partial_update", "update"):
            return FolderUpdateSerializer
        return FolderSerializer

    @action(detail=True, methods=["post"])
    def scan(self, request: Request, pk: uuid.UUID) -> Response:
        folder = self.get_object()
        return Response(
            {"status": "queued", "folder_id": str(folder.id)},
            status=202,
        )
