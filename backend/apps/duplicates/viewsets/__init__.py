"""Duplicates APIs: list, detail, resolution plan."""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from apps.duplicates.models import DuplicateGroup
from apps.duplicates.serializers import DuplicateGroupSerializer


class DuplicateGroupViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = DuplicateGroupSerializer
    queryset = DuplicateGroup.objects.prefetch_related("members", "members__file")

    @action(detail=True, methods=["post"])
    def resolve(self, request: Request, pk) -> Response:
        return Response(
            {"status": "plan_created", "group_id": str(pk)}, status=status.HTTP_202_ACCEPTED
        )
