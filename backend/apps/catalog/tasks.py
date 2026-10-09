"""Celery scan task for catalog indexing."""

from __future__ import annotations

from celery import shared_task
from sortiq_fs.walker import walk

from apps.catalog.models import File
from apps.folders.models import Folder
from apps.jobs.models import Job


@shared_task(bind=True, max_retries=3)
def scan_folder_task(self, folder_id: str, job_id: str) -> dict:
    folder = Folder.objects.get(id=folder_id)
    job = Job.objects.get(id=job_id)

    job.status = "running"
    job.stage_name = "walking"
    job.save(update_fields=["status", "stage_name"])

    scan_start = folder.last_scanned_at or folder.created_at

    entries, stats = walk(
        folder.path, recursive=folder.recursive, follow_symlinks=folder.follow_symlinks
    )
    indexed = 0
    updated = 0
    skipped = 0
    deleted = 0
    bytes_scanned = 0

    for entry in entries:
        if job.status == "cancelled":
            job.status = "cancelled"
            job.save(update_fields=["status"])
            return {"folder_id": folder_id, "status": "cancelled", "indexed": indexed}

        try:
            existing = File.objects.filter(
                folder=folder, relative_path=entry.relative_path, deleted_at__isnull=True
            ).first()

            if existing is not None:
                if (
                    existing.size_bytes == entry.size_bytes
                    and existing.mtime_ns == entry.mtime_ns
                    and existing.inode_identity == entry.inode
                ):
                    existing.last_seen_at = entry.mtime_ns
                    existing.save(update_fields=["last_seen_at"])
                    skipped += 1
                    continue
                else:
                    existing.size_bytes = entry.size_bytes
                    existing.mtime_ns = entry.mtime_ns
                    existing.ctime_ns = entry.ctime_ns
                    existing.inode_identity = entry.inode
                    existing.hash_stage = "none"
                    existing.save()
                    updated += 1
            else:
                File.objects.create(
                    folder=folder,
                    relative_path=entry.relative_path,
                    canonical_path=entry.absolute_path,
                    name=entry.name,
                    extension=entry.name.split(".")[-1].lower() if "." in entry.name else "",
                    size_bytes=entry.size_bytes,
                    mtime_ns=entry.mtime_ns,
                    ctime_ns=entry.ctime_ns,
                    inode_identity=entry.inode,
                    is_directory=entry.is_directory,
                    is_symlink=entry.is_symlink,
                )
                indexed += 1

            bytes_scanned += entry.size_bytes
        except Exception:
            pass

    # Soft-delete missing files
    missing = File.objects.filter(
        folder=folder, deleted_at__isnull=True, last_seen_at__lt=scan_start
    )
    deleted = missing.update(deleted_at=__import__("django.utils.timezone").timezone.now())

    folder.last_scanned_at = __import__("django.utils.timezone").timezone.now()
    folder.save(update_fields=["last_scanned_at"])

    job.status = "completed"
    job.stage_name = "finalizing"
    job.progress_percent = 100
    job.metrics = {
        "files_indexed": indexed,
        "files_updated": updated,
        "files_skipped": skipped,
        "files_deleted": deleted,
        "bytes_scanned": bytes_scanned,
    }
    job.save(update_fields=["status", "stage_name", "progress_percent", "metrics"])

    return {"folder_id": folder_id, "status": "completed", "indexed": indexed}
