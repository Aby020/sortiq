from django.contrib import admin

from apps.catalog.models import Category, File


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "is_system", "created_at")
    list_filter = ("is_system",)
    search_fields = ("slug", "name")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "folder", "extension", "size_bytes", "hash_stage")
    list_filter = ("hash_stage", "is_directory", "deleted_at")
    search_fields = ("name", "canonical_path")
    readonly_fields = ("sha256", "first_seen_at", "last_seen_at")
