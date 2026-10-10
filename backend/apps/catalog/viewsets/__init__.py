"""Catalog and files APIs with user scoping."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import filters, mixins, permissions, viewsets

from apps.catalog.models import Category, File
from apps.catalog.models_metadata import FileMetadata
from apps.catalog.serializers import (
    CategorySerializer,
    FileMetadataSerializer,
    FileSerializer,
)


class UserScopedViewSetMixin:
    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, self.queryset.all(), 'folder__user')


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet:
        from apps.core.services.desktop_scope import user_scope
        return user_scope(self.request, Category.objects.all(), 'files__folder__user').distinct()


class FileViewSet(
    UserScopedViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = FileSerializer
    queryset = File.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "extension"]
    ordering_fields = ["name", "size_bytes", "last_seen_at"]

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(deleted_at__isnull=True)
            .select_related("folder", "category")
        )


class FileMetadataViewSet(
    UserScopedViewSetMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    serializer_class = FileMetadataSerializer
    queryset = FileMetadata.objects.all()

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related("file__folder")
