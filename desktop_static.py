"""Static SPA file server for the Sortiq desktop runtime.

Serves the built React bundle from ``frontend/dist`` with a single-page
application fallback (``/`` and any non-file route resolve to
``index.html``), and proxies ``/api`` and ``/service`` requests to the
local control and execution planes so the frontend can call them
same-origin without CORS configuration.

Pure Python; no Django imports.
"""

from __future__ import annotations

import http.server
import logging
import mimetypes
import socket
import urllib.error
import urllib.request
from pathlib import Path
from threading import Thread

logger = logging.getLogger("sortiq.desktop.static")

DEFAULT_INDEX = "index.html"
API_PREFIXES = ("/api/", "/service/")


class _ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """Static handler with SPA fallback and API reverse proxy."""

    # Set by the server factory.
    api_targets: dict[str, str] = {}
    dist_dir: Path = Path(".")
    index_path: Path = Path("index.html")

    def log_message(self, fmt: str, *args) -> None:  # noqa: D102
        logger.debug("[static] %s", fmt % args)

    def _send_not_found(self) -> None:
        self.send_error(404, "Not Found")

    def _proxy(self) -> None:
        for prefix, target in self.api_targets.items():
            if self.path.startswith(prefix):
                upstream = target.rstrip("/") + self.path
                try:
                    req = urllib.request.Request(upstream, method=self.command)
                    for header in ("Content-Type", "Accept"):
                        value = self.headers.get(header)
                        if value:
                            req.add_header(header, value)
                    if self.command in ("POST", "PUT", "PATCH"):
                        length = int(self.headers.get("Content-Length", 0) or 0)
                        body = self.rfile.read(length) if length else None
                        req.data = body
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        payload = resp.read()
                        self.send_response(resp.status)
                        for key, value in resp.getheaders():
                            if key.lower() in (
                                "content-type",
                                "content-length",
                                "cache-control",
                            ):
                                self.send_header(key, value)
                        self.send_header("Content-Length", str(len(payload)))
                        self.end_headers()
                        if self.command != "HEAD":
                            self.wfile.write(payload)
                except urllib.error.HTTPError as exc:
                    payload = exc.read()
                    self.send_response(exc.code)
                    self.send_header(
                        "Content-Type",
                        exc.headers.get("Content-Type", "application/json"),
                    )
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    if self.command != "HEAD":
                        self.wfile.write(payload)
                except (OSError, urllib.error.URLError) as exc:
                    logger.warning("proxy error for %s: %s", self.path, exc)
                    self.send_error(502, f"upstream unavailable: {exc}")
                return
        self._send_not_found()

    def do_GET(self) -> None:  # noqa: N802
        self._serve()

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve()

    def do_POST(self) -> None:  # noqa: N802
        self._proxy()

    def do_PUT(self) -> None:  # noqa: N802
        self._proxy()

    def do_PATCH(self) -> None:  # noqa: N802
        self._proxy()

    def do_DELETE(self) -> None:  # noqa: N802
        self._proxy()

    def _resolve_static(self) -> Path | None:
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/"):
            return self.index_path
        relative = path.lstrip("/")
        candidate = (self.dist_dir / relative).resolve()
        try:
            candidate.relative_to(self.dist_dir.resolve())
        except ValueError:
            return None
        if candidate.is_file():
            return candidate
        if candidate.is_dir():
            index = candidate / DEFAULT_INDEX
            if index.is_file():
                return index
        return None

    def _serve(self) -> None:
        if self.path.startswith(API_PREFIXES):
            self._proxy()
            return

        target = self._resolve_static()
        if target is None:
            # SPA fallback: client-side routing resolves the route.
            target = self.index_path

        try:
            payload = target.read_bytes()
        except OSError:
            self._send_not_found()
            return

        mime_type, _ = mimetypes.guess_type(str(target))
        self.send_response(200)
        self.send_header(
            "Content-Type", mime_type or "application/octet-stream"
        )
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)


class StaticServer(Thread):
    """Run the SPA/static server in a daemon thread."""

    def __init__(
        self,
        dist_dir: Path,
        port: int,
        api_targets: dict[str, str] | None = None,
    ) -> None:
        super().__init__(name="sortiq-static", daemon=True)
        self.dist_dir = dist_dir
        self.port = port
        self.api_targets = api_targets or {}
        self._httpd: http.server.ThreadingHTTPServer | None = None
        self.error: Exception | None = None

    def run(self) -> None:
        handler = type(
            "BoundHandler",
            (_ProxyHandler,),
            {
                "dist_dir": self.dist_dir,
                "index_path": self.dist_dir / DEFAULT_INDEX,
                "api_targets": self.api_targets,
            },
        )
        try:
            self._httpd = http.server.ThreadingHTTPServer(
                ("127.0.0.1", self.port), handler
            )
        except OSError as exc:
            self.error = exc
            logger.error("static server bind failed on %s: %s", self.port, exc)
            return
        logger.info("Serving frontend at http://127.0.0.1:%s", self.port)
        self._httpd.serve_forever(poll_interval=0.5)

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()

    def wait_ready(self, timeout: float = 10.0) -> bool:
        import time

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.error is not None:
                return False
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                try:
                    sock.connect(("127.0.0.1", self.port))
                    return True
                except OSError:
                    time.sleep(0.1)
        return False
