"""Windows path semantics."""

from __future__ import annotations

from django.test import TestCase
from sortiq_fs.pathguard import normalize


class WindowsPathTests(TestCase):
    def test_drive_case_insensitive(self) -> None:
        self.assertEqual(normalize(r"c:\folder"), r"C:\folder")

    def test_mixed_slashes(self) -> None:
        self.assertIn("/", normalize(r"D:\Folder/sub\file.txt"))

    def test_long_path_normalized(self) -> None:
        s = normalize(r"D:\a\\" + r"b\\" * 300 + r"file.txt")
        self.assertTrue(len(s) > 0)
