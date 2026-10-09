from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Catalog bounded context."""

    name = "apps.catalog"
    default_auto_field = "django.db.models.BigAutoField"
