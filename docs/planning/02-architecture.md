# 02 — Sortiq System Architecture

> Working directory: `D:\AbiLabs\Sortiq`
> This document proposes the delivery architecture: service boundaries, the
> local filesystem integration strategy, background jobs, API design, security,
> testing, development/deployment, observability, technical risks, and the set
> of **decisions that need your approval** before implementation starts.
> The implementation order is in [`03-roadmap.md`](03-roadmap.md).

---

## 1. Decisions requiring approval

These are the non-obvious calls. Everything else in this doc follows normal
defaults. Each becomes an ADR in `docs/decisions/` once approved.

### D1 — Desktop integration: **no Electron/Tauri in v1** *(recommended)*

**Problem.** The mandate says "desktop-first" and "interact safely with the
user's local filesystem" — but the mandatory stack is a browser React app plus
Python/Django/FastAPI. A browser can't reach the local filesystem by itself.

**Proposal.** Treat the Python backend as a **local-first service** that _runs on
the user's machine_ (`localhost`), owns all filesystem I/O, and serves the React
app. The conceptual "Desktop/local integration layer" from the Task is realized
as:

```
React SPA (Vite) ── HTTP/JSON ──► Django/DRF (control plane, localhost)
                                     │  ├─ PostgreSQL, Redis
                                     │  └─► FastAPI (execution plane) ──► filesystem
                                     Celery workers (background) ──► filesystem
```

The frontend therefore **never** touches the filesystem directly (no File System
Access API). Folder selection is server-driven: `GET /fs/roots` (drives) + `GET
/fs/browse` (safe directory walk) → `POST /folders`.

**Why this is correct without a desktop framework:**
- Full capability (scan/hash/move/rollback everything) is achieved with the
  mandated stack; Electron/Tauri would add a second runtime + a second
  distribution model and duplicate what a localhost server already provides.
- The safety-critical code lives once, in Python, fully unit-tested — the same
  code in the browser would be a security downgrade.
- The same backend can later be deployed as a home server with zero UI change.
- **Optional enhancement (Phase 14):** wrap the SPA + localhost backend in a
  **Tauri** shell for a native window, tray, auto-start, and a native folder
  picker — without touching the architecture. This is a packaging decision, not
  an architecture one, and can be deferred safely.

**Trade-off you are accepting:** until the Tauri wrapper exists, the "desktop"
experience is a browser tab at `http://localhost`. For a portfolio project that
prioritizes clean engineering and testability, this is the right trade.

> ✅ / ❌ — please confirm D1.

### D2 — Django/DRF vs FastAPI boundaries (the "don't use both redundantly" rule)

Two processes, **no overlap of responsibilities**:

| | Django + DRF — **control plane** | FastAPI — **execution plane** |
| --- | --- | --- |
| Job | System of record. Auth, users, folders, rules, suggestions, operations ledger, jobs, activities, analytics queries. The only API the SPA needs for application state. | High-throughput, I/O-bound filesystem work: directory listing, scan walking, hashing, metadata extraction, MIME sniffing, duplicate grouping, storage aggregation, and **execution** of operation plans (the actual `move/rename/delete`). |
| Why FastAPI is genuinely better here | — | asyncio concurrency for many-file I/O; streaming (NDJSON/SSE) progress; cheap per-task cancellation; internal service, not public. |
| Schema ownership | **PostgreSQL schema — all tables, via Django migrations** | No owned schema. Reads selected rows via SQLAlchemy Core (read-mostly), writes only its own measurement rows if needed, created by Django migrations. |
| Auth | Full user auth (JWT), object-level authz | Internal service-token only; no user models; validates the distinct service key on every call |
| Frontend reach | Primary | Only via Django proxy for interactive reads (explorer listing, live status) — or never directly |
| Invocation | Handles requests; enqueues Celery tasks; calls FastAPI for interactive fs read paths | Called by Django synchronously (small interactive ops) and by Celery workers for the long-running parts of jobs |

This separation is **justified by throughput and by the async model**, not by
feeling. A scan of 100k files is exactly the case where sync Django ORM per-row
is wrong and asyncio streaming matters.

### D3 — Redis/Celery vs FastAPI (no processing redundancy)

- **Celery + Redis = job *orchestration***: durable, retryable, cancellable,
  scheduled work — full scans, dedupe runs, automation jobs, analytics
  snapshots, organization runs. Owns the job lifecycle/visibility the SPA shows.
- **FastAPI = job *execution*** (and interactive streaming): Celery workers call
  the FastAPI service (or the shared engine directly) to actually do filesystem
  I/O. FastAPI is stateless and re-entrant; Celery provides idempotency and
  scheduling.
- Shared, safety-critical library `sortiq_fs` (walker, hasher, PathGuard,
  operation executor, watcher) is imported by **both** — so there is exactly one
  implementation of every fs rule, unit-tested independently of either process.

### D4 — MIME/`watchdog`/MIME deps (the only proposed additions)

- `filetype` (pure-Python content sniff) + stdlib `mimetypes` + custom sniffer —
  avoids bundling libmagic on Windows.
- `watchdog` for folder **change events** → enqueues incremental re-index jobs.
  Polling fallback exists for unusual filesystems. Justification: the product
  requires "monitor folders for changes"; rebuild from scratch is unnecessary.
- No other runtime deps proposed beyond the mandated stack + the ordinary
  utility set (`django-environ`, `drf-spectacular`, `structlog`, `django-unfold`
  optional admin skin, `factory-boy`/`pytest-asyncio`/`hypothesis` for tests).

---

## 2. System topology (boxes)

```
┌─────────────────────────────────────────────────────────────┐
│  Browser: React SPA (Vite) · TS · Tailwind · Motion         │
│  TanStack Query · Zustand · Radix · react-virtual           │
└───────────────┬─────────────────────────────────────────────┘
                │ HTTP /api/v1 (JWT)                (interactive reads via DRF proxy)
                ▼
┌──────────────────────────────────────────────────────────────┐
│ Django + DRF — CONTROL PLANE (localhost:8000)               │
│ auth · folders · rules · suggestions · operations · jobs ·  │
│ activities · analytics · fs-roots/browse · admin            │
│ ── owns PostgreSQL schema (migrations); serves SPA (prod)   │
├──────────────────────────────────────────────────────────────┤
│         │ calls                              │ enqueues      │
│         ▼                                   ▼                │
│  FastAPI — EXECUTION PLANE       Redis + Celery (workers,    │
│  (localhost:8100, service-token)  beat) — ORCHESTRATION      │
│  scan streams · hashing · MIME · │                            │
│  metadata · dup grouping ·       │ celery tasks invoke the   │
│  operation execute/rollback      │ FastAPI service / shared  │
└──────────────┬───────────────────┘ sortiq_fs engine          │
               │                ▲                                │
               ▼                └──────────── shared package ───┘
        Local filesystem   (walker · hasher · pathguard ·
        (managed roots)      operation executor · watcher)
┌──────────────────────────────────────────────────────────────┐
│ PostgreSQL (localhost:5432)   Redis (localhost:6379)          │
└──────────────────────────────────────────────────────────────┘
```

Dev process tree (`scripts/dev.ps1` starts all): Django `runserver` :8000 ·
FastAPI `uvicorn :8100` · Celery worker · Celery beat · Vite :5173 (proxy
`/api` → :8000, `/fs-api` → :8100) · postgres/redis via Docker Compose or
portable installs.

---

## 3. Local filesystem integration strategy

1. **Backend owns the filesystem.** All reads/writes go through the Python
   engine (`sortiq_fs`) inside Django/FastAPI/Celery processes running on the
   user's machine. No browser FS access in v1.
2. **Folder selection is safe and server-side**: `GET /fs/roots` lists
   acceptable roots (Windows drives; POSIX `/`, `~` with display), `GET
   /fs/browse?path=` walks a directory (depth-limited, deny-list aware) for
   pickers; `POST /folders` validates with PathGuard before registering.
3. **Scanning**: full default, then **incremental** — each scan diffs against
   the index using fingerprints `(size, mtime_ns, inode_identity)`, so only new
   or changed paths are hashed/classified. `watchdog` creates change events
   between scans → debounced incremental jobs.
4. **Execution**: only through the operations engine (§6 of doc 01). FastAPI
   executes item-by-item with stat-before-act and journaling.
5. **Watcher**: `watchdog` observer per active folder (configurable on/off);
   events coalesced into `reindex_file`/`rescan_folder` Celery tasks. Polling
   fallback for exotic filesystems.

---

## 4. Background job architecture (Redis + Celery)

### 4.1 Job lifecycle & states (task-mandated set, mapped to Celery)

```
PENDING ──► RUNNING ──► COMPLETED
   │             │──► FAILED            (retriable transient errors w/ backoff)
   │             └──► CANCELLED         (cooperative + forced tail)
   └──► CANCELLED/PENDING (never starts)
```

- **Progress**: worker writes `progress_pct`, `progress_stage`
  (walking/indexing/hashing/classifying/finalizing), per-stage `counts`, and a
  `heartbeat_at` every few seconds to the `jobs` row and Redis. The SPA polls
  `GET /jobs/{id}` (or an SSE stream for live scans).
- **Idempotency**: job dedupe key `(kind, folder_id, params_hash)` — a RUNNING or
  same-spec job is not re-enqueued; worker tasks begin by validating the job is
  still `PENDING` (`update … WHERE state='PENDING'` CAS).
- **Retries**: Celery retry with exponential backoff for transient failures
  (locked files on Windows, permission flicker, DB blips) up to N; terminal
  errors mark `FAILED` with `error` JSON; per-file errors are counted, not fatal.
- **Cancellation**: SPA → `POST /jobs/{id}/cancel` sets `requested_cancel`; the
  worker checks it between items and inside long hashes (cooperative). Celery
  revoke is used only as the final forced tail after a grace period. Cancel
  leaves the journal consistent (in-flight item completes).
- **Crash recovery**: on worker startup, jobs found `RUNNING` with a stale
  heartbeat are re-marked `FAILED`/requeued; `.operation_items` with
  `outcome=pending` are reconciled against the DB (complete or rollback).
- **Beat**: periodic maintenance (purge/retention, suggestion refresh,
  scheduled automation rules, analytics snapshot refresh).

### 4.2 Job kinds

`scan` · `duplicate` · `classify` · `analyze` · `automate` · `organize`
(organize = executing an operation plan in the background).

---

## 5. API design

Versioned at `/api/v1` from day one (URL versioning). JSON; consistent error
envelope; paginated lists; explicit request/response models (DRF serializers +
drf-spectacular OpenAPI).

### 5.1 Error envelope

```json
{ "error": { "code": "validation_error", "message": "…",
             "details": { "field": "…" }, "request_id": "…", "status": 400 } }
```

Consistent code taxonomy: `auth_*`, `not_found`, `permission_denied`,
`validation_error`, `conflict`, `job_invalid_state`, `fs_*`, `internal`.

### 5.2 Authentication & authorization

- **JWT** (short-lived access + refresh), returned on login/register; stored by
  the SPA and sent in `Authorization: Bearer`. No CSRF needed for bearer API
  (same-origin serving in prod). Rate-limited refresh.
- **Bootstrap login**: first run generates a one-time local bootstrap token
  printed to the terminal / settings screen for the SPA's initial login
  (avoids shipping a default password).
- **Object-level authz**: every queryset scoped to the authenticated user
  (no IDOR); service token scoped to FastAPI only; folders/operations/jobs are
  owned by a user.
- **Protected endpoints**: everything except `register`/`login`/`refresh`/`health`.
- **Throttling**: login/register/refresh and expensive endpoints.

### 5.3 Endpoint map (Django/DRF — control plane)

```
Auth         POST /auth/register · /auth/login · /auth/refresh · /auth/logout
             GET  /auth/me
Folders      GET|POST /folders · GET|PATCH|DELETE /folders/{id}
             POST /folders/{id}/scan → 202 {job_id} · GET /folders/{id}/scan-status
             GET  /folders/{id}/explore?path=          (live listing + index marks)
Files        GET /files?folder&q&category&ext&min_size&max_size&modified_after&sort
             GET /files/{id} · GET /files/{id}/metadata · POST /files/search
             GET /files/{id}/actions                    (available safe actions)
Duplicates   GET /duplicates?folder&status · GET /duplicates/{group_id}
             POST /duplicates/{group_id}/resolve  {keeper_file_id, action}
Categories   GET /categories
Suggestions  GET /suggestions?status&rule · POST /suggestions/{id}/accept
             POST /suggestions/{id}/dismiss
Rules        GET|POST /rules · GET|PATCH|DELETE /rules/{id}
             POST /rules/{id}/preview · POST /rules/reorder
Operations   GET /operations · POST /operations (from plan) · GET /operations/{id}
             GET /operations/{id}/items · POST /operations/{id}/execute
             POST /operations/{id}/cancel · POST /operations/{id}/rollback
Jobs         GET /jobs?kind&state · GET /jobs/{id} · POST /jobs/{id}/cancel
Analytics    GET /analytics/overview · /storage · /duplicates · /empties
Activities   GET /activities?limit&cursor
Settings     GET|PATCH /settings
Fs           GET /fs/roots · GET /fs/browse?path=
Health       GET /health/   (db, redis, service tokens, celery ping)
```

FastAPI **internal** endpoints (service-token):
`POST /internal/fs/list-tree` · `/internal/fs/scan-stream` (NDJSON) ·
`/internal/fs/hash-batch` · `/internal/fs/mime` · `/internal/fs/metadata-extract` ·
`/internal/fs/classify-batch` · `/internal/fs/duplicates/group` ·
`/internal/fs/operation/execute` · `/internal/fs/operation/rollback` ·
`GET /internal/health`.

### 5.4 API design rules

- Explicit serializer fields (never `__all__`); read vs write serializers where
  shapes differ; no internal fields (no hash_error exposure beyond need).
- `PageNumberPagination` for lists, documented limits; keyset for deep pages.
- Filter via validated query params (`django-filter`).
- Every mutation of disk state goes through Operations; suggestion/rule actions
  produce a plan (never direct fs calls from a serializer).

---

## 6. Security strategy

Risk → control (baseline: `standards/security`). The gate: no open
Critical/High at review.

| Risk (from Task) | Control |
| --- | --- |
| Arbitrary filesystem access | PathGuard allowlist (managed roots only) + deny-list (system/home/drive roots) applied on every fs call; service-token on the execution plane; fs work only via registered folders |
| Path traversal | Canonicalize + reject `..`, separators abuse, NUL/control chars, length caps; property-tested corpus |
| Symlinks / junctions | Not followed for scans by default; mutation never dereferences link targets; containment check against resolved path; Windows reparse-point handling |
| Unauthorized operations | Object-level authz (user-scoped querysets); operation scope re-validated at execution; concurrent-overlap refusal |
| Malicious filenames | No shell interpolation ever; `os` APIs only; careful handling of case/collisions; logs escape-encoded |
| Permissions | Per-item error accounting (`permission_denied` code), retry-able, never fatal |
| Uploaded/imported data | v1 takes paths only, no binary upload surface |
| API auth | JWT + bootstrap token + rate limits/lockout on credential endpoints |
| Secrets | `.env` gitignored, `.env.example` committed; keys from env at runtime; `pip-audit`/`npm audit`/`grype` in CI; nothing secret in logs |
| CORS | Allow `http://localhost:5173` (dev) + same-origin in prod |
| CSRF | Bearer-JWT APIs (no cookie), so no CSRF surface; if sessions are added later, CSRF enforced |
| DB credentials | Env; never logged |
| Background-task abuse | Job input validation against schema; bound to authed user; idempotent CAS start; cooperative cancel; no unauthenticated job trigger |
| Secrets in UI | Frontend never holds service tokens or DB creds |
| Observability of attacks | Structured audit events in `activities`; request-id correlation |

---

## 7. Testing strategy

Follows `standards/testing` (pyramid, ≥80% new code, deterministic, filesystem
tests in isolated tmp trees).

| Layer | Approach |
| --- | --- |
| `sortiq_fs` unit | pytest, `tmp_path` + `TreeBuilder` fixtures (real files/symlinks/junctions); **never** scans real user dirs |
| PathGuard | unit + **property tests (hypothesis):** random paths → correct allow/deny; adversarial corpus (traversal, symlink chains, junctions) |
| Hasher/duplicates | golden fixtures; large-file streaming; chunk equivalence; changing-during-scan; permission/missing-file races |
| Operation engine | preview/conflict policies · partial failure · rollback precondition checks · **crash-recovery** (fake journal mid-point) · cancellation between items |
| Classifier | per-signal unit tests + integration vector; rule-override precedence; confidence thresholds; determinism (same input → same output) |
| Django tests | `TestCase` + factories; view/API tests for auth, authz (IDOR), validation; `override_settings` for configs |
| Celery | eager-mode logic tests + Redis integration for lifecycle/cancel/retry; `makemigrations --check` in CI |
| FastAPI | `pytest-asyncio` for streaming endpoints, service-token auth, cancellation |
| Frontend component | Vitest + Testing Library; MSW mocks the API layer; token/theme/a11y basics |
| Frontend integration/e2e | Playwright happy paths against a disposable local stack + temp dirs (scan → explore → dedupe → preview → execute → rollback) |

Deterministic data: factories over hand-rolled fixtures; `freezegun` for
time-dependent logic; no shared mutable state; no real network (MSW/pytest
mocks); CI runs on **Windows** (dev platform) and Linux (container) to catch
platform-specific fs behavior.

---

## 8. Observability, error handling, DX

- **Logging**: `structlog` JSON; request-id middleware; correlated across
  Django/FastAPI/Celery (same request/job id).
- **Error reporting**: safe error envelope to clients; full stack traces kept
  local; `activity` audit events for domain/security events; never log secrets,
  paths with full PII only in redacted form where sensitive.
- **Health**: `/health/` (Django) and `/internal/health` (FastAPI) checking DB,
  Redis, worker heartbeat; `healthz` for probes.
- **Development experience**: `.env.example` documented; `uv`-managed venv +
  `pyproject.toml`; `ruff` + `ruff format` + `mypy` + pre-commit; `pytest`;
  `drf-spectacular` schema; `scripts/*.ps1` bootstrap/dev/lint/test/db-reset
  helpers; Docker Compose for postgres+redis; Vite dev proxy. CI on every PR:
  lint → typecheck → tests → audits → migrations-check → frontend build →
  bundle budget.
- **Config**: Django `settings/base.py` + `dev.py` + `prod.py` via
  `django-environ`; `.env.example` only in git.

---

## 9. Development / packaging / deployment

Dev: local-first (described above). Prod/deploy path (Phase 14) follows
`standards/devops`: **gunicorn** (web) + celery worker + celery beat behind
nginx/Caddy; SPA collected via `collectstatic`; Postgres/Redis via compose or a
managed instance; migrations as a release step before traffic; deploy from
SemVer tags; rollback = previous tag; `DEBUG=False`, `ALLOWED_HOSTS`, TLS.
Packaging: `bootstrap.ps1` provisions a local machine (venv, compose services,
migrations, start-all, open browser); optional **Tauri** shell (D1) as the
"real desktop" packaging.

---

## 10. Technical risks & mitigations

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Windows-specific fs behavior (locking, junctions, case) | High | Engine tests on Windows CI; PathGuard tests for reparse points; quarantine on same volume to avoid cross-device | 
| Files mutate during scans/ops | High | Stat-before/after discipline; "changed during scan" skip + requeue; journal recovery |
| Scan of very large trees (hundreds of k files) | Medium | Incremental diffs on fingerprints; streaming walker; bounded memory hashing; keyset pagination; background jobs + progress |
| Undo/rollback under-drives expectations | Medium | Product copy is honest: "best-effort rollback with safety preconditions"; per-item conflict reporting |
| Two-schema ownership (Django + FastAPI) drift | Medium | Single owner (Django); FastAPI SQLAlchemy Core read-only by convention + a review gate on any FastAPI write path |
| Celery + FastAPI being seen as redundant | Medium | Explicit orchestration vs execution split (D3); documented in ARCHITECTURE.md |
| Portfolio scope creep (too many screens) | High | Screen list frozen in doc 01; roadmap builds in dependency order; each phase reviewable |
| AI feature temptation | High | No AI by default; a clearly gated inference seam; "no fake AI" rule in product spec |

---

## 11. What should be built first

Highest-leverage, dependency-respecting order (expanded in the roadmap):

1. **Foundations** — independent git repo, monorepo layout, tooling/CI, dev env,
   two hello-world services + health endpoints.
2. **Domain model + migrations** — the Postgres schema from doc 01 with tests.
3. **`sortiq_fs` core** — PathGuard, walker, hasher, operation primitives
   (unit/property tested before any UI exists). This is where product safety
   lives and it must exist before anything else touches disk.
4. **Scan pipeline end-to-end (thin vertical slice)** — folder → scan job →
   index rows → explore endpoint → a minimal SPA screen showing results.
5. Everything else hangs off that spine: duplicates → classification →
   operations engine → suggestions/rules → automation → remaining screens →
   hardening → packaging.

---

*Next: [`03-roadmap.md`](03-roadmap.md) — the phased implementation roadmap with
small, independently reviewable tasks.*