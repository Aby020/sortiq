"""URL routing for the authentication app."""

from __future__ import annotations

from django.urls import path

from apps.authentication import views

app_name = "authentication"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("refresh/", views.RefreshView.as_view(), name="refresh"),
    path("me/", views.MeView.as_view(), name="me"),
]
