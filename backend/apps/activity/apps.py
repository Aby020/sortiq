from django.apps import AppConfig


class ActivityConfig(AppConfig):
    """Activity bounded context."""

    name = "apps.activity"
    default_auto_field = "django.db.models.BigAutoField"
