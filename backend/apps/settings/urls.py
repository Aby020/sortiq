"""URLs for settings."""
from __future__ import annotations

from apps.settings.viewsets import SettingsView
from django.urls import path

urlpatterns = [path("", SettingsView.as_view(), name="settings")]
