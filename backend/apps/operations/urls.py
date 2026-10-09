"""URLs for $app."""
from django.urls import path, include
from apps.$app.viewsets import $(echo $app | sed 's/./\U&/' | tr '[:lower:]' '[:upper:]')ViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'', $app)  # placeholder - real wire in config
urlpatterns = [path("", include(router.urls))]
