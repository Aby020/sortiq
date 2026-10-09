"""URLs for activity."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.activity.viewsets import ActivityViewSet

router = DefaultRouter()
router.register(r'', ActivityViewSet, basename='activity')
urlpatterns = [path("", include(router.urls))]
