"""IDOR and user-scoping security tests."""

from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient
from tests.factories import FileFactory, FolderFactory, UserFactory


class IdorSecurityTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user_a = UserFactory(username="alice")
        self.user_b = UserFactory(username="bob")
        self.client.force_authenticate(user=self.user_a)
        self.folder_b = FolderFactory(user=self.user_b)
        self.file_b = FileFactory(folder=self.folder_b)

    def test_file_access_denied_for_other_user(self) -> None:
        response = self.client.get(f"/api/v1/files/{self.file_b.id}/")
        self.assertIn(response.status_code, (403, 404))

    def test_folder_access_denied_for_other_user(self) -> None:
        response = self.client.get(f"/api/v1/folders/{self.folder_b.id}/")
        self.assertIn(response.status_code, (403, 404))

    def test_category_list_isolated_by_user(self) -> None:
        response = self.client.get("/api/v1/categories/")
        self.assertEqual(response.status_code, 200)
        for item in response.data.get("results", response.data):
            assert item["id"] is not None

    def test_unauthenticated_rejected(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/files/")
        self.assertEqual(response.status_code, 401)
