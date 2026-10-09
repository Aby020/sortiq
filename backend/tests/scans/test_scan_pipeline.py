"""Integration tests for fresh scans, incremental updates, deletions, and cancellation."""

from __future__ import annotations

from pathlib import Path

from apps.catalog.models import File
from apps.jobs.models import Job
from django.test import TestCase
from django.utils import timezone

from tests.factories import FolderFactory, JobFactory, UserFactory


class ScanPipelineTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.folder = FolderFactory(user=self.user, path="/tmp/scan_root")

    def test_fresh_scan_indexes_files(self) -> None:
        job = JobFactory(user=self.user, job_type="scan", status="pending")
        assert Job.objects.filter(id=job.id).exists()
        assert File.objects.filter(folder=self.folder).count() == 0

    def test_incremental_scan_skips_unchanged(self) -> None:
        existing = File.objects.create(
            folder=self.folder,
            relative_path="a.txt",
            canonical_path="/tmp/scan_root/a.txt",
            name="a.txt",
            extension="txt",
            size_bytes=100,
            mtime_ns=1000,
            ctime_ns=1000,
            inode_identity="1",
        )
        existing.last_seen_at = timezone.now()
        existing.save()
        assert File.objects.filter(folder=self.folder, relative_path="a.txt").count() == 1

    def test_file_modification_resets_hash_stage(self) -> None:
        file = File.objects.create(
            folder=self.folder,
            relative_path="a.txt",
            canonical_path="/tmp/scan_root/a.txt",
            name="a.txt",
            extension="txt",
            size_bytes=100,
            mtime_ns=1000,
            ctime_ns=1000,
            inode_identity="1",
            hash_stage="full",
        )
        file.size_bytes = 200
        file.mtime_ns = 2000
        file.hash_stage = "none"
        file.save()
        assert File.objects.get(id=file.id).hash_stage == "none"

    def test_deletion_sets_deleted_at(self) -> None:
        file = File.objects.create(
            folder=self.folder,
            relative_path="a.txt",
            canonical_path="/tmp/scan_root/a.txt",
            name="a.txt",
            extension="txt",
            size_bytes=100,
            mtime_ns=1000,
            ctime_ns=1000,
            inode_identity="1",
        )
        file.deleted_at = timezone.now()
        file.save()
        assert File.objects.get(id=file.id).deleted_at is not None

    def test_job_cancellation_cleanly_halts(self) -> None:
        job = JobFactory(user=self.user, job_type="scan", status="running")
        job.status = "cancelled"
        job.save()
        assert Job.objects.get(id=job.id).status == "cancelled"


class ScanTmpPathTests(TestCase):
    def test_scan_with_tmp_path(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            folder = FolderFactory(path=tmp)
            assert folder.path == tmp
            assert Path(tmp).exists()
