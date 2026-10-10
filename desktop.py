"""Sortiq desktop launcher.

Runs the local control plane (Django) and execution plane (FastAPI) in-process,
then presents the built React frontend inside a native pywebview window.

Usage:
    python desktop.py

The database is stored in the user data directory:
    %LOCALAPPDATA%\\Sortiq\\sortiq.db
"""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="{levelname} {asctime} {module} {message}",
    style="{",
)
logger = logging.getLogger("sortiq.desktop")

APP_NAME = "Sortiq"
APP_VERSION = "1.0.0"

REPO_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"

# User data directory: %LOCALAPPDATA%\Sortiq
USER_DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home() / ".local") or Path.home()) / APP_NAME
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = USER_DATA_DIR / "sortiq.db"

DJANGO_PORT = 8000
FASTAPI_PORT = 8100


def _free_port(start: int, fallback: int = 0) -> int:
    """Return a free TCP port, preferring ``start``."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", start))
            return start
        except OSError:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _configure_django_env() -> None:
    """Point Django at the desktop database and disable server-only settings."""

    # Force the desktop profile (no host header surprises, no CORS issues).
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
    # Local single-user desktop: no external auth tokens required.
    os.environ.setdefault("INTERNAL_SERVICE_TOKEN", "local-desktop")
    os.environ["DEBUG"] = "False"
    os.environ.setdefault("LOG_LEVEL", "INFO")
    # Silence the Django development server banner noise.
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"

    sys.path.insert(0, str(BACKEND_DIR))

    import django

    django.setup()

    from django.core.management import call_command

    logger.info("Applying database migrations to %s", DB_PATH)
    call_command("migrate", "--run-syncdb", verbosity=0)


def _run_django(port: int) -> subprocess.Popen:
    """Launch the Django control plane as an in-process subprocess."""

    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    env["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
    env["DEBUG"] = "False"

    cmd = [
        sys.executable,
        "-m",
        "django",
        "runserver",
        f"127.0.0.1:{port}",
        "--noreload",
        "--insecure",
    ]
    logger.info("Starting control plane on http://127.0.0.1:%s", port)
    return subprocess.Popen(
        cmd,
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def _run_fastapi(port: int) -> subprocess.Popen:
    """Launch the FastAPI execution plane as an in-process subprocess."""

    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    env["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "service.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    logger.info("Starting execution plane on http://127.0.0.1:%s", port)
    return subprocess.Popen(
        cmd,
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def _await_ready(port: int, timeout: float = 30.0) -> bool:
    """Wait until the given port accepts connections."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.25)
    return False


def _log_stream(stream, source: str) -> None:
    """Forward a subprocess stream into the desktop log."""

    for line in stream or []:
        logger.debug("[%s] %s", source, line.rstrip())


def main() -> None:
    if not FRONTEND_DIST.exists() or not (FRONTEND_DIST / "index.html").exists():
        logger.error(
            "Frontend build not found at %s. Run `npm run build` in frontend/ first.",
            FRONTEND_DIST,
        )
        sys.exit(1)

    _configure_django_env()

    django_port = _free_port(DJANGO_PORT)
    fastapi_port = _free_port(FASTAPI_PORT)

    django_proc = _run_django(django_port)
    fastapi_proc = _run_fastapi(fastapi_port)

    for proc, source in ((django_proc, "django"), (fastapi_proc, "fastapi")):
        threading.Thread(target=_log_stream, args=(proc.stdout, source), daemon=True).start()

    if not _await_ready(django_port):
        logger.error("Control plane failed to start on port %s", django_port)
        django_proc.terminate()
        fastapi_proc.terminate()
        sys.exit(1)
    if not _await_ready(fastapi_port):
        logger.error("Execution plane failed to start on port %s", fastapi_port)

    import webview

    logger.info("Opening Sortiq desktop window")
    window = webview.create_window(
        title=f"{APP_NAME} {APP_VERSION}",
        url=f"http://127.0.0.1:{django_port}/",
        width=1280,
        height=800,
        min_size=(960, 600),
        resizable=True,
    )
    webview.start(gui="winforms", private_mode=False)

    django_proc.terminate()
    fastapi_proc.terminate()
    try:
        django_proc.wait(timeout=5)
        fastapi_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        django_proc.kill()
        fastapi_proc.kill()


if __name__ == "__main__":
    main()
