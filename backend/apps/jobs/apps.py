from django.apps import AppConfig


class JobsConfig(AppConfig):
    """Jobs bounded context."""

    name = "apps.jobs"
    default_auto_field = "django.db.models.BigAutoField"
