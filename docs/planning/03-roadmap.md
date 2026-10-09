# 03 — Sortiq Implementation Roadmap

> Working directory: `D:\AbiLabs\Sortiq`
> Companion docs: [00-reference-analysis](00-reference-analysis.md) ·
> [01-product-design](01-product-design.md) · [02-architecture](02-architecture.md)
>
> Rule: **each phase is a reviewable unit.** Every task is PR-sized, merged via
> `feature/<name>` off `main` (Conventional Commits), ships with tests + docs,
> and passes the review gate before the next phase starts. No task is started
> until you approve the prior phase.

---

## Phase 0 — Architecture & planning (this package)

**Objective:** lock the design decisions and validate the reference analysis
before any code.

- [ ] You review this planning package (`docs/planning/00…03`).
- [ ] Approve the four decisions in `02-architecture.md` §1 (D1–D4) — most
      importantly **D1: no Electron/Tauri in v1** and the Django/FastAPI split.
- [ ] Approve the screen list and domain model in `01-product-design.md`.
- [ ] Reify approved decisions as ADRs in `docs/decisions/` (adr-001 … adr-004)
      per `standards/documentation.md`.
- [ ] Write `README.md` (package-level) + `.gitignore` at the Sortiq root.

**Gate:** your written approval on decisions + screen list. Phase 1 does not
start without it.

---

## Phase 1 — Repository & project foundation

**Objective:** a clean, reproducible monorepo with two live services and green CI.

- [ ] Initialize Sortiq as an **independent git repository** at `D:\AbiLabs\Sortiq`
      (currently an untracked folder inside the AbiLabs meta-repo) — history
      starts fresh; `main` protected; branch policy per `git-workflow.md`.
- [ ] Scaffold monorepo layout (see `02-architecture.md` §2):
      `backend/` (Django project `config/`, apps in `backend/apps/`,
      `backend/sortiq_fs/` package), `frontend/` (Vite React TS), `scripts/`,
      `docs/`.
- [ ] `uv`-managed Python env (src layout), `pyproject.toml` (ruff, mypy, pytest,
      black/isort via ruff format), pinned deps, `.env.example` committed.
- [ ] Django project (`config/settings/base|dev|prod.py`, `django-environ`) +
      FastAPI service (`backend/service/`) each with `/health/` + `/internal/health`.
- [ ] `docker-compose.yml` for dev Postgres + Redis; `scripts/bootstrap.ps1`
      (provision venv + services + migrate + start-all + open browser),
      `scripts/dev.ps1`, `scripts/lint.ps1`, `scripts/test.ps1`.
- [ ] GitHub Actions CI: lint → mypy → pytest → `makemigrations --check` →
      dep audit (`pip-audit`, `npm audit`) → frontend build.
- [ ] Auth skeleton: user model, JWT register/login/refresh/me + bootstrap token.

**Gate:** clean checkout → `bootstrap.ps1` runs → `/health/` green → CI green.

---

## Phase 2 — Database & domain layer

**Objective:** the entire Postgres schema (doc 01 §7) with migrations, factories,
and model tests. No disk operations yet.

- [ ] Django apps per bounded context (naming per `standards/django`):
      `users`, `folders`, `catalog` (files/metadata/categories/duplicates),
      `rules` (rules/suggestions), `operations`, `jobs`, `core`
      (activities/settings).
- [ ] Models + migrations for **all** tables in doc 01 §7; review SQL
      (`sqlmigrate`) per migration; constraints/indexes/partial indexes as speced.
- [ ] Seed data migration for `categories` taxonomy.
- [ ] `factory_boy` factories; model/constraint tests (uniqueness on
      `(folder_id, path_lower)` partial index, CHECK constraints, FK integrity).
- [ ] `makemigrations --check` wired into CI.

**Gate:** migrations apply clean on a fresh DB; constraint/factory tests green.

---

## Phase 3 — Filesystem engine core (`sortiq_fs`)

**Objective:** the safety-critical core, fully tested, *before* any UI or scan
job. All tests operate only on `tmp_path` trees.

- [ ] `sortiq_fs/paths.py` — **PathGuard**: canonicalize, allowlist/deny-list
      containment, traversal/symlink/junction rejection, recursion guard.
      Property tests (hypothesis) + adversarial corpus.
- [ ] `sortiq_fs/walker.py` — streaming walker (per-folder, skip symlinks by
      default, permission-tolerant, cancellation callback, depth control).
- [ ] `sortiq_fs/hasher.py` — size fingerprinting, partial (head+tail) and full
      SHA-256 streaming, sparse aware, `changed-during-read` detection,
      cancellable; tests incl. large-file chunking and race fixtures.
- [ ] `sortiq_fs/metadata.py` — MIME sniff (`filetype` + mimetypes + custom) and
      header/EXIF-lite extraction; graceful on missing/odd files.
- [ ] `sortiq_fs/ops.py` — **operation primitives**: stat-before-act, single-item
      move/copy/rename/soft-delete-to-quarantine, per-item outcomes
      (permission/conflict/missing/changed); unit + crash-recovery tests.
- [ ] `sortiq_fs/watcher.py` — `watchdog` observer wrapper + polling fallback,
      coalesces events to change records. (Tests use the polling fallback.)

**Gate:** engine fully unit/property-tested; no non-test code path can touch a
path outside an allowlist.

---

## Phase 4 — Scan & indexing pipeline (thin vertical slice)

**Objective:** the first end-to-end capability: register a folder → background
scan → indexed files → a minimal SPA screen reads them.

- [ ] `jobs` lifecycle service (PENDING→RUNNING→…→done, progress writes,
      heartbeat, CAS start, requested-cancel) + Celery scan task.
- [ ] Scan task: walk (Phase 3) → diff vs index (fingerprint) → upsert `files`,
      soft-delete missing → optional hash/classify sub-stages.
- [ ] Folder API: `GET|POST /folders`, `GET /fs/roots`, `GET /fs/browse`,
      `POST /folders/{id}/scan`, `GET /folders/{id}/scan-status` (jobs).
- [ ] Incremental re-scan on `watchdog` events (debounced) + manual "Scan now".
- [ ] Frontend foundation: Vite+React+TS, Router, TanStack Query + Zustand, Tailwind
      tokens (light/dark), layout shell (sidebar/topbar).
- [ ] **Scan Center screen** (folders, add-folder picker via `/fs/browse`, scan
      jobs with live progress + cancel) and a minimal **Explore** list (files +
      status chips). Loading/empty/error states.

**Gate:** add a `tmp`-prepared folder, scan it, files appear in the SPA with
real progress; cancellation works mid-scan.

---

## Phase 5 — Duplicate detection

- [ ] Dedupe pipeline (doc 01 §5): size grouping → fingerprint short-circuit →
      partial hash → full hash → group assembly; incremental re-hash only
      changed files.
- [ ] Persist `sha256`/`partial_hash`/`hash_stage`/`hash_verified_at`;
      invalidation on change events; `duplicate_groups` + members.
- [ ] `GET /duplicates` (+ filters) · group detail · `POST
      /duplicates/{group_id}/resolve` → prepares a **quarantine operation plan**
      (never executes directly).
- [ ] **Duplicates screen** (groups, reclaimable bytes, resolve dialog) +
      **Storage Analytics screen v1** (duplicate overhead tile, large files).
- [ ] Celery `duplicate` job with progress/cancel/retry; analytics of
      reclaimable bytes.

**Gate:** golden-file duplicate fixtures → correct groups; a re-scan does not
re-hash unchanged files (verify via instrumentation); resolve → plan preview.

---

## Phase 6 — Classification & intelligence

- [ ] Classification service: signal registry (extension/mime/filename/context/
      size/time/metadata) with weights, confidence vector, threshold,
      `Unclassified` fallback, rule-override precedence; `categories` data.
- [ ] InferenceSignal **seam** only (no provider wired in v1; documented gate for
      future AI, per AI/NLP standard).
- [ ] `GET /categories`; classify runs inside scan/classify jobs; store
      `category_id/confidence/signals` on `files`; reclassify only deltas on
      rule-version bump.
- [ ] **Explore enhancements** (category chips, filter by category/unclassified);
      classification unit + determinism tests.

**Gate:** a mixed scratch folder classifies deterministically to correct
categories; unclassifiable files land in `Unclassified` (no guessing).

---

## Phase 7 — Full API layer (control plane)

**Objective:** complete, documented, safe `/api/v1` for everything the SPA needs.

- [ ] DRF serializers/viewsets for files, suggestions, rules, operations, jobs,
      activities, analytics, settings per `02-architecture.md` §5.3 — explicit
      fields, object-level authz, pagination, filters, error envelope,
      throttling.
- [ ] drf-spectacular OpenAPI schema; endpoint tests across
      auth/AuthZ/validation/error paths (incl. IDOR attempts).
- [ ] `django-admin` minimal (readonly, list/search) for operations/jobs only.

**Gate:** schema renders; full authz test matrix green (no IDOR).

---

## Phase 8 — Background jobs & operational services

- [ ] Celery bespoke jobs: `analyze` (storage aggregation snapshots), `automate`
      (scheduled rules), maintenance/retention beat tasks; job dedupe, retry
      with backoff, cooperative + forced cancel, crash recovery sweep.
- [ ] FastAPI execution service wired for real: scan-stream (NDJSON), hash-batch,
      mime/metadata/classify-batch, duplicate grouping, op execute/rollback;
      service-token auth; synchronous small-op path from Django; streaming
      progress to SPA.

**Gate:** volume test (a generated 20–50k-file tree) scans with bounded memory;
cancel/retry/recovery behave; no schema drift between Django and FastAPI reads.

---

## Phase 9 — Safe operations engine + Operations UI

**Objective:** the flagship safety surface — plan, preview, execute, rollback.

- [ ] Operations orchestration: plan builder (scope+filters/rules), conflict
      detection/resolution, WAL journal writes, per-item stat-before-act
      execution loop, partial-failure ledger, cooperative cancel.
- [ ] Rollback: precondition-checked reverse replay, own audit record,
      conflict reporting; crash-recovery reconciliation tests.
- [ ] Quarantine service (managed `.sortiq` folder per volume; no unlink default).
- [ ] **Operations screen**: history/detail/item ledger, execute/cancel/rollback,
      preview shown inline; **Settings** quarantine + hashing defaults.
- [ ] Operation-related API from Phase 7 wired end-to-end.

**Gate:** scripted scenario — organize folder, kill the process mid-run, restart
→ journal reconciles; rollback honors modified-file safety preconditions.

---

## Phase 10 — Suggestions, Rules & Automation

- [ ] Rule engine: matchers, action spec, priority evaluation, dry-run match,
      version bumps; rule CRUD + reorder + preview endpoints.
- [ ] Suggestions generator (heuristics + matched rules, confidence/reason);
      accept → builds operation plan; dismiss; no re-appearance.
- [ ] **Suggestions screen** and **Rules & Automation screen**
      (condition/action editor, dry-run results, scheduled-apply toggle).
- [ ] Celery `automate` job (apply approved rule patterns on-scan / on-schedule)
      — always via operations engine.

**Gate:** simulated folder produces sensible suggestions; rules match
deterministically; automation applies only what was previewed.

---

## Phase 11 — Remaining screens & UX polish

- [ ] **Dashboard** (stats + quick actions + recent activity), **Activity**
      screen (feed, filtering), **Storage Analytics** full (category/extension/
      time charts, empty-folder report) — `dataviz` skill for the charts.
- [ ] Explore: full filters/sort/search/CSV export, metadata drawer.
- [ ] Accessibility pass (keyboard nav, focus, `prefers-reduced-motion`, screen
      reader labels) across all screens; responsive at ≥400px; design-card
      review via `ui-ux-pro-max` skill.

**Gate:** keyboard/mouse walkthrough of every flow; a11y basic audit green.

---

## Phase 12 — Security hardening & observability

- [ ] Security review passes (`security-engineer` gate): secret scan, dependency
      audit, OWASP checklist, adversarial path tests, rate-limit proof, CORS/
      header config, bootstrap-token lifetime.
- [ ] Structured logging (`structlog`) + request-id correlation across the three
      processes; audit events complete; log redaction (no secrets/full PII).
- [ ] `/health/` + heartbeat dashboards; error-reporting hygiene.

**Gate:** no open Critical/High; audit trail covers every fs mutation.

---

## Phase 13 — Testing & QA hardening

- [ ] Full test suite audit: coverage gate ≥80% on new code; fill gaps in
      duplicates/ops/classification/API/frontend component integration.
- [ ] E2E happy paths (Playwright) against disposable stack + temp dirs: onboarding
      → scan → dedupe → preview → execute → rollback; CI runs the Windows matrix.
- [ ] Property tests consolidated (PathGuard, classifier determinism, journal
      invariants); performance sanity (scan throughput profile documented).

**Gate:** suite green locally + CI; coverage report reviewed; E2E recorded.

---

## Phase 14 — Packaging & production polish

- [ ] Production layout per `standards/devops`: gunicorn (web) + worker (Celery) +
      beat, nginx/Caddy serving SPA + static + proxies; `DEBUG=False`,
      ALLOWED_HOSTS, TLS ready; deploy-from-tag pipeline + rollback; `Dockerfile`/
      `.dockerignore`.
- [ ] Full documentation set: `README.md` (quickstart clone→running),
      `ARCHITECTURE.md`, `API.md` (from OpenAPI), `DATABASE.md`,
      `SECURITY.md`, `DEVELOPMENT.md`, `TESTING.md`, `CONTRIBUTING.md`,
      `docs/runbooks/*`, ADRs — kept in sync with code.
- [ ] Optional **[D1] Tauri shell** (native window/tray/auto-start/native folder
      picker) if approved earlier — packaging only, no architecture change.
- [ ] Release checklist: tag `v1.0.0`, artifacts, demo scenario script.

**Gate:** clean machine bootstrap → full product demo runs → docs match code.

---

## Definition of done (every phase)

- [ ] Meets its stated objective; no task carries over silently.
- [ ] All new behavior tested (per `standards/testing`); lint/type/tests/audit CI green.
- [ ] No open Critical/High security finding on anything touching auth or disk.
- [ ] Docs/ADRs updated in the same change.
- [ ] You reviewed and approved the phase before the next begins.

---

**End of planning package.** No application code has been written. Waiting for
your review of: the four architecture decisions (esp. **D1 desktop strategy**),
the screen list, the domain model, and this roadmap — before Phase 1 begins.