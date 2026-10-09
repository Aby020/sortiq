"""Domain model tests."""

from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.factories import (
    CategoryFactory,
    DuplicateGroupFactory,
    FileFactory,
    FolderFactory,
    OrganizationRuleFactory,
)


class FolderModelTests(TestCase):
    def test_create_folder(self) -> None:
        folder = FolderFactory()
        assert isinstance(folder.id, uuid.UUID)
        assert folder.is_active is True
        assert folder.created_at is not None
        assert folder.updated_at is not None

    def test_str(self) -> None:
        folder = FolderFactory(name="MyFolder")
        assert str(folder) == "MyFolder"


class CategoryModelTests(TestCase):
    def test_slug_unique(self) -> None:
        CategoryFactory(slug="docs")
        with self.assertRaises(Exception):
            CategoryFactory(slug="docs")

    def test_str(self) -> None:
        cat = CategoryFactory(name="Documents")
        assert str(cat) == "Documents"


class FileModelTests(TestCase):
    def test_uuid_primary_key(self) -> None:
        file = FileFactory()
        assert isinstance(file.id, uuid.UUID)

    def test_size_bytes_non_negative(self) -> None:
        file = FileFactory(size_bytes=0)
        file.full_clean()
        assert file.size_bytes == 0

    def test_unique_relative_path_when_active(self) -> None:
        folder = FolderFactory()
        FileFactory(folder=folder, relative_path="a.txt")
        with self.assertRaises(Exception):
            FileFactory(folder=folder, relative_path="a.txt")

    def test_same_path_allowed_after_soft_delete(self) -> None:
        folder = FolderFactory()
        original = FileFactory(folder=folder, relative_path="a.txt")
        original.deleted_at = "2024-01-01T00:00:00Z"
        original.save()
        replacement = FileFactory(folder=folder, relative_path="a.txt")
        assert replacement.pk != original.pk

    def test_hash_stage_choices(self) -> None:
        file = FileFactory(hash_stage="partial")
        assert file.hash_stage == "partial"


class DuplicateGroupModelTests(TestCase):
    def test_sha256_unique(self) -> None:
        DuplicateGroupFactory(sha256="a" * 64)
        with self.assertRaises(Exception):
            DuplicateGroupFactory(sha256="a" * 64)

    def test_size_bytes_validator(self) -> None:
        group = DuplicateGroupFactory(size_bytes=-1)
        with self.assertRaises(ValidationError):
            group.full_clean()


class OrganizationRuleModelTests(TestCase):
    def test_create(self) -> None:
        rule = OrganizationRuleFactory()
        assert rule.is_active is True
        assert rule.priority == 0
