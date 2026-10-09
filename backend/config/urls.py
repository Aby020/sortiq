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

if settings.DEBUG:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
