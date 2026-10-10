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
    permission_classes = [permissions.AllowAny]
    serializer_class = ActivitySerializer

    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, Activity.objects.all(), 'user')
