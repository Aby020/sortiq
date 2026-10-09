"""URLs for catalog."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.viewsets import CategoryViewSet, FileMetadataViewSet, FileViewSet

router = DefaultRouter()
router.register(r'categories/', CategoryViewSet, basename='category')
router.register(r'files/', FileViewSet, basename='file')
router.register(r'file-metadata/', FileMetadataViewSet, basename='filemetadata')
urlpatterns = [path("", include(router.urls))]
