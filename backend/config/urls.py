"""URL routing for the Sortiq control plane."""

from __future__ import annotations

from apps.authentication import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/folders/", include("apps.folders.urls")),
    path("api/v1/files/", include("apps.catalog.urls")),
    path("api/v1/categories/", include("apps.catalog.urls")),
    path("api/v1/duplicates/", include("apps.duplicates.urls")),
    path("api/v1/rules/", include("apps.rules.urls")),
    path("api/v1/suggestions/", include("apps.suggestions.urls")),
    path("api/v1/operations/", include("apps.operations.urls")),
    path("api/v1/jobs/", include("apps.jobs.urls")),
    path("api/v1/activity/", include("apps.activity.urls")),
    path("api/v1/settings/", include("apps.settings.urls")),
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("health/", auth_views.health_view, name="health"),
]

if settings.DEBUG and "debug_toolbar" in getattr(settings, "INSTALLED_APPS", []):
    try:
        import debug_toolbar  # noqa: F401

        urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
    except ImportError:
        pass

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
