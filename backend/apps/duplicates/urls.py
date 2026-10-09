"""URLs for duplicates."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.duplicates.viewsets import DuplicateGroupViewSet

router = DefaultRouter()
router.register(r'', DuplicateGroupViewSet, basename='duplicategroup')
urlpatterns = [path("", include(router.urls))]
