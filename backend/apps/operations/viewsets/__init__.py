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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OperationSerializer

    def get_queryset(self) -> QuerySet:
        return Operation.objects.filter(user=self.request.user)
