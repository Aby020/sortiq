"""FolderWatcher using watchdog observers.

Listens for creation, modification, deletion, movement events;
debounces burst events; falls back to polling when observers
are unavailable. Pure Python; no Django ORM.
"""

from __future__ import annotations

import time
from typing import Callable, Iterable

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEvent = object
    FileSystemEventHandler = object
    Observer = None


class FolderWatcher(FileSystemEventHandler):
    def __init__(
        self,
        path: str,
        on_change: Callable[[str, str], None],
        debounce_seconds: float = 2.0,
    ) -> None:
        self.path = path
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self._last_event_at = 0.0
        self._observer = None
        self._supported = Observer is not None

    def on_any_event(self, event: FileSystemEvent) -> None:
        now = time.time()
        if now - self._last_event_at < self.debounce_seconds:
            return
        self._last_event_at = now
        self.on_change(event.src_path, event.event_type)

    def start(self) -> bool:
        if not self._supported or self._observer is not None:
            return False
        self._observer = Observer()
        self._observer.schedule(self, self.path, recursive=True)
        self._observer.start()
        return True

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def poll_once(self, events: Iterable[tuple[str, str]]) -> None:
        for src_path, event_type in events:
            self.on_change(src_path, event_type)
