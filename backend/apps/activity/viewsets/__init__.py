"""Activity APIs with user scoping."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import mixins, permissions, viewsets

from apps.activity.models import Activity
from apps.activity.serializers import ActivitySerializer


class ActivityViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivitySerializer

    def get_queryset(self) -> QuerySet:
        return Activity.objects.filter(user=self.request.user)
