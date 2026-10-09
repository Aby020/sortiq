"""App configuration for the authentication app."""

from __future__ import annotations

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuration for the authentication app."""

    name = "apps.authentication"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals  # noqa: F401
