from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AuthEndpointsTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_register_endpoint(self) -> None:
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
                "password_confirm": "newpass123",
            },
            format="json",
        )
        assert response.status_code == 201
        assert "tokens" in response.data
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_password_mismatch(self) -> None:
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "mismatchuser",
                "email": "mismatch@example.com",
                "password": "pass123",
                "password_confirm": "different",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health/")
        assert response.status_code in (200, 503)
        assert "status" in response.data
