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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationSuggestionSerializer

    def get_queryset(self) -> QuerySet:
        return OrganizationSuggestion.objects.filter(user=self.request.user)
