"""Classification engine tests."""

from __future__ import annotations

from django.test import TestCase

from apps.catalog.classification.engine import (
    ClassificationEngine,
    ExtensionSignal,
    FilenameContextSignal,
    MimeSignal,
)
from apps.catalog.models import Category, File
from apps.folders.models import Folder
from tests.factories import FolderFactory


class SignalTests(TestCase):
    def setUp(self) -> None:
        self.folder = FolderFactory()

    def test_extension_signal(self) -> None:
        signal = ExtensionSignal()
        file = File(folder=self.folder, name="doc.pdf", extension="pdf")
        self.assertEqual(signal.evaluate(file), "documents")

    def test_mime_signal(self) -> None:
        signal = MimeSignal()
        file = File(folder=self.folder, name="img.jpg", mime_type="image/jpeg")
        self.assertEqual(signal.evaluate(file), "images")

    def test_filename_context_signal(self) -> None:
        signal = FilenameContextSignal()
        file = File(folder=self.folder, name="README.md")
        self.assertEqual(signal.evaluate(file), "documents")


class EngineTests(TestCase):
    def setUp(self) -> None:
        self.folder = FolderFactory()
        self.engine = ClassificationEngine()

    def test_extension_classification(self) -> None:
        file = File.objects.create(
            folder=self.folder,
            relative_path="doc.pdf",
            canonical_path="/f/doc.pdf",
            name="doc.pdf",
            extension="pdf",
        )
        self.engine.apply(file)
        file.refresh_from_db()
        assert file.category is not None
        assert file.category.slug == "documents"

    def test_mime_fallback(self) -> None:
        file = File.objects.create(
            folder=self.folder,
            relative_path="photo.img",
            canonical_path="/f/photo.img",
            name="photo.img",
            extension="img",
            mime_type="image/png",
        )
        self.engine.apply(file)
        file.refresh_from_db()
        assert file.category is not None
        assert file.category.slug == "images"

    def test_unclassified_fallback(self) -> None:
        file = File.objects.create(
            folder=self.folder,
            relative_path="data.xyz",
            canonical_path="/f/data.xyz",
            name="data.xyz",
            extension="xyz",
        )
        self.engine.apply(file)
        file.refresh_from_db()
        assert file.category is not None
        assert file.category.slug == "unclassified"
        assert file.category.is_system is True
