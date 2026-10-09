"""Operations API URLs."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.operations.viewsets import OperationViewSet

router = DefaultRouter()
router.register(r"", OperationViewSet, basename="operation")

urlpatterns = [path("", include(router.urls))]
