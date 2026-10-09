# Sortiq

Sortiq is an intelligent desktop file management platform. It scans local folders, deduplicates files with a staged hashing pipeline, classifies content via a multi-signal engine, and executes safe, journaled organization plans that can be rolled back with full audit fidelity.

## Architecture

Sortiq runs a **dual-plane** backend:

- **Django + DRF** is the control plane (auth, REST API, persistence).
- **FastAPI** is the internal execution plane (high-throughput scan streaming, batch hashing) protected by a shared service token.
- **Celery + Redis** drives asynchronous scans and scheduled maintenance.
- **sortiq_fs** is a pure-Python filesystem engine with path containment (`PathGuard`), staged hashing, and quarantine primitives that never delete data.

Every mutation flows through the **Operations Engine** — a WAL-journaled planner that verifies state *before* acting, persists each step, and rolls back by reversing journal entries while preserving audit history.

## Quickstart

```bash
# Control plane
cd backend
uv sync --all-extras
DJANGO_SETTINGS_MODULE=config.settings.base PYTHONPATH=backend python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.base PYTHONPATH=backend python manage.py runserver

# Internal execution plane
uvicorn service.main:app --host 0.0.0.0 --port 8100

# Frontend
cd frontend && npm install && npm run build
```

## Engineering highlights

- Staged duplicate detection: size grouping → partial hash (1 MiB) → full SHA-256
- Multi-signal classification: extension, MIME, filename context, deterministic fallback
- Stat-before-act: every operation verifies source state immediately before mutation
- IDOR protection: every viewset scopes `get_queryset()` by `request.user`
- Correlation IDs: `X-Request-ID` bound to structlog JSON context per request
- Quarantine-only: the engine rejects `delete` actions (`NotImplementedError`)
