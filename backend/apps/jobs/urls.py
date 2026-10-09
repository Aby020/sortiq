"""URLs for jobs."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.jobs.viewsets import JobViewSet

router = DefaultRouter()
router.register(r'', JobViewSet, basename='job')
urlpatterns = [path("", include(router.urls))]
