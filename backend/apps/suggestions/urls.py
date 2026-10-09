"""URLs for suggestions."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.suggestions.viewsets import OrganizationSuggestionViewSet

router = DefaultRouter()
router.register(r"", OrganizationSuggestionViewSet, basename="suggestion")
urlpatterns = [path("", include(router.urls))]
