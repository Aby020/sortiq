"""Rules APIs with user scoping."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import mixins, permissions, viewsets

from apps.rules.models import OrganizationRule
from apps.rules.serializers import OrganizationRuleSerializer


class OrganizationRuleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrganizationRuleSerializer

    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, OrganizationRule.objects.all(), 'user')

    def perform_create(self, serializer) -> None:
        from apps.core.services.desktop_scope import effective_user
        serializer.save(user=effective_user(self.request))
