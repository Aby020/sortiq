from django.contrib import admin

from apps.folders.models import Folder


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "user", "is_active", "last_scanned_at")
    list_filter = ("is_active", "is_watched", "recursive", "follow_symlinks")
    search_fields = ("name", "path")
