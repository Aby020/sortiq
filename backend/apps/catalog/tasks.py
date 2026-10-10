"""Native FastAPI background jobs (replaces Celery shared tasks)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from django.utils import timezone

from apps.catalog.models import File
from apps.folders.models import Folder
from apps.jobs.models import Job

_executor = ThreadPoolExecutor(max_workers=4)


def run_scan(folder_id: str, job_id: str) -> dict:
    """Execute a filesystem scan synchronously in the FastAPI thread pool."""

    folder = Folder.objects.get(id=folder_id)
    job = Job.objects.get(id=job_id)

    job.status = "running"
    job.stage_name = "walking"
    job.save(update_fields=["status", "stage_name"])

    scan_start = folder.last_scanned_at or folder.created_at

    from sortiq_fs.walker import walk

    entries, stats = walk(
        folder.path, recursive=folder.recursive, follow_symlinks=folder.follow_symlinks
    )
    indexed = 0
    updated = 0
    skipped = 0
    deleted = 0
    bytes_scanned = 0

    # Locked / restricted entries are already captured by the walker;
    # record them in the job journal so the UI can surface them.
    skipped += stats.skipped
    if stats.errors:
        import logging

        logger = logging.getLogger(__name__)
        for err in stats.errors:
            logger.info("scan skipped item: %s", err)

    for entry in entries:
        job.refresh_from_db(fields=["status"])
        if job.status == "cancelled":
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
            continue

    missing = File.objects.filter(
        folder=folder, deleted_at__isnull=True, last_seen_at__lt=scan_start
    )
    deleted = missing.update(deleted_at=timezone.now())

    folder.last_scanned_at = timezone.now()
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
        "locked_or_inaccessible": stats.skipped,
        "scan_errors": stats.errors,
    }
    job.save(update_fields=["status", "stage_name", "progress_percent", "metrics"])

    return {"folder_id": folder_id, "status": "completed", "indexed": indexed}


def dispatch_scan(folder_id: str, job_id: str) -> None:
    """Schedule a scan on the native background thread pool."""

    _executor.submit(run_scan, folder_id, job_id)


def maintenance() -> dict:
    """Queue scans for folders stale for over 7 days."""

    stale = Folder.objects.filter(
        last_scanned_at__lt=timezone.now() - timezone.timedelta(days=7),
        is_active=True,
    )
    queued = 0
    for folder in stale[:10]:
        job = Job.objects.create(
            user=folder.user,
            job_type="scan",
            status="pending",
            stage_name="queued_by_beat",
        )
        dispatch_scan(str(folder.id), str(job.id))
        queued += 1
    return {"stale_folders": stale.count(), "queued": queued}
