"""Suggestions APIs with user scoping."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import mixins, permissions, viewsets

from apps.suggestions.models import OrganizationSuggestion
from apps.suggestions.serializers import OrganizationSuggestionSerializer


class OrganizationSuggestionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrganizationSuggestionSerializer

    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, OrganizationSuggestion.objects.all(), 'user')
