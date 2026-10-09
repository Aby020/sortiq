"""URLs for rules."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.rules.viewsets import OrganizationRuleViewSet

router = DefaultRouter()
router.register(r'', OrganizationRuleViewSet, basename='rule')
urlpatterns = [path("", include(router.urls))]
