"""URLs for folders."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.folders.viewsets import FolderViewSet

router = DefaultRouter()
router.register(r"", FolderViewSet, basename="folder")
urlpatterns = [path("", include(router.urls))]
