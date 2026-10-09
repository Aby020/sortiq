"""Seed system category taxonomy."""

from __future__ import annotations

from django.db import migrations

SYSTEM_CATEGORIES = [
    ("documents", "Documents", "Document files", "📄", "#3B82F6"),
    ("images", "Images", "Image files", "🖼️", "#10B981"),
    ("videos", "Videos", "Video files", "🎬", "#EF4444"),
    ("audio", "Audio", "Audio files", "🎵", "#8B5CF6"),
    ("archives", "Archives", "Archive files", "📦", "#F59E0B"),
    ("code-dev", "Code & Dev", "Source code and development files", "💻", "#6366F1"),
    ("executables", "Executables & Installers", "Executable files and installers", "⚙️", "#64748B"),
    ("system-config", "System & Config", "System and configuration files", "🔧", "#78716C"),
    ("unclassified", "Unclassified", "Fallback category", "❓", "#9CA3AF"),
]


def seed_categories(apps, schema_editor):  # noqa: ANN001
    Category = apps.get_model("catalog", "Category")
    for slug, name, description, icon, color in SYSTEM_CATEGORIES:
        Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "icon": icon,
                "color": color,
                "is_system": True,
            },
        )


def unseed_categories(apps, schema_editor):  # noqa: ANN001
    Category = apps.get_model("catalog", "Category")
    Category.objects.filter(is_system=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
