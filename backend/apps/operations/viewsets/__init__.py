"""Operations APIs with user scoping."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import mixins, permissions, viewsets

from apps.operations.models import Operation
from apps.operations.serializers import OperationSerializer


class OperationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = OperationSerializer

    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, Operation.objects.all(), 'user')
