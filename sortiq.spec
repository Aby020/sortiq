# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec bundling Sortiq into a standalone Sortiq.exe.

Build:
    pyinstaller sortiq.spec

Output:
    dist\\Sortiq.exe  — single-file desktop runtime with frontend/dist embedded.
"""

import os
from pathlib import Path

block_cipher = None

ROOT = Path(os.path.dirname(os.path.abspath(SPEC)))  # noqa: F821
BACKEND = ROOT / "backend"
FRONTEND_DIST = ROOT / "frontend" / "dist"

# Collect production frontend assets and expose them as data files.
frontend_assets = []
if FRONTEND_DIST.exists():
    for path in FRONTEND_DIST.rglob("*"):
        if path.is_file():
            dest = os.path.join("frontend", "dist", path.relative_to(FRONTEND_DIST).as_posix())
            frontend_assets.append((str(path), os.path.dirname(dest)))

# Bundle the backend package tree (config + apps + service + sortiq_fs).
hiddenimports = [
    "config",
    "config.settings",
    "config.settings.base",
    "config.settings.development",
    "config.settings.production",
    "apps",
    "apps.authentication",
    "apps.authentication.apps",
    "apps.authentication.signals",
    "apps.folders",
    "apps.catalog",
    "apps.duplicates",
    "apps.rules",
    "apps.suggestions",
    "apps.operations",
    "apps.jobs",
    "apps.activity",
    "apps.settings",
    "service",
    "service.main",
    "service.main_internal",
    "sortiq_fs",
    # Django / DRF runtime imports that PyInstaller cannot trace statically
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "django_celery_results",
    "watchdog",
    "structlog",
    "environ",
    "filetype",
    "requests",
    "uvicorn",
    "fastapi",
]

datas = frontend_assets + [
    (str(BACKEND / "sortiq_fs"), "sortiq_fs"),
]

a = Analysis(
    ["desktop.py"],
    pathex=[str(ROOT), str(BACKEND)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Sortiq",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
