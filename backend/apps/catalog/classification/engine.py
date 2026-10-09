"""Signal registry and evaluator pipeline."""

from __future__ import annotations

from typing import Protocol

from apps.catalog.models import File


class Signal(Protocol):
    def evaluate(self, file: File) -> str | None:
        ...


class ExtensionSignal:
    EXT_MAP = {
        "pdf": "documents", "docx": "documents", "txt": "documents",
        "jpg": "images", "png": "images", "gif": "images",
        "mp4": "videos", "mkv": "videos",
        "mp3": "audio", "wav": "audio",
        "zip": "archives", "tar": "archives",
        "py": "code-dev", "js": "code-dev", "ts": "code-dev",
        "exe": "executables", "msi": "executables", "dmg": "executables",
        "ini": "system-config", "cfg": "system-config", "yaml": "system-config",
    }

    def evaluate(self, file: File) -> str | None:
        ext = file.extension.lower() if file.extension else ""
        return self.EXT_MAP.get(ext)


class MimeSignal:
    MIME_MAP = {
        "application/pdf": "documents",
        "image/": "images",
        "video/": "videos",
        "audio/": "audio",
        "application/zip": "archives",
        "application/x-python-code": "code-dev",
    }

    def evaluate(self, file: File) -> str | None:
        mime = file.mime_type or ""
        for prefix, slug in self.MIME_MAP.items():
            if mime.startswith(prefix):
                return slug
        return None


class FilenameContextSignal:
    def evaluate(self, file: File) -> str | None:
        name = file.name.lower() if file.name else ""
        if "readme" in name or "license" in name:
            return "documents"
        if "config" in name or ".env" in name:
            return "system-config"
        return None


class ClassificationEngine:
    def __init__(self) -> None:
        self.signals: list[Signal] = [
            ExtensionSignal(),
            MimeSignal(),
            FilenameContextSignal(),
        ]

    def classify(self, file: File) -> str:
        for s in self.signals:
            result = s.evaluate(file)
            if result:
                return result
        return "unclassified"

    def apply(self, file: File) -> None:
        slug = self.classify(file)
        from apps.catalog.models import Category as CategoryModel
        category, _ = CategoryModel.objects.get_or_create(
            slug=slug,
            defaults={"name": slug.replace("-", " ").title(), "is_system": slug == "unclassified"},
        )
        file.category = category
        file.save(update_fields=["category"])
