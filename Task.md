# SORTIQ — Active Sprint: Phase 6 (Multi-Signal Classification) & Phase 7 (Complete REST API)

## Status: IN PROGRESS
- [x] Phase 1: Repository Foundation, Dev Environment & Auth Skeleton
- [x] Phase 2: Database Domain Model & Migrations
- [x] Phase 3: Filesystem Engine (`sortiq_fs`)
- [x] Phase 4: Folder Registration, Scanning Pipeline & React Scan Center
- [x] Phase 5: Staged Duplicate Detection Engine, Resolution & UI
- [/] Phase 6: Multi-Signal Classification Engine (`apps/catalog/classification/`)
  - [ ] Sub-Task 6.1: Signal Registry & Evaluator Pipeline
  - [ ] Sub-Task 6.2: Category Assignment & Deterministic Fallback
  - [ ] Sub-Task 6.3: Classification Integration into Scan Pipeline
  - [ ] Sub-Task 6.4: Classification Test Suite (`backend/tests/classification/`)
- [/] Phase 7: Complete DRF API Surface & Security Hardening
  - [ ] Sub-Task 7.1: Catalog & Files API (`/api/v1/files/`, `/api/v1/categories/`)
  - [ ] Sub-Task 7.2: Rules & Suggestions API (`/api/v1/rules/`, `/api/v1/suggestions/`)
  - [ ] Sub-Task 7.3: Operations & Audit History API (`/api/v1/operations/`, `/api/v1/activity/`)
  - [ ] Sub-Task 7.4: User Preferences & System Settings API (`/api/v1/settings/`)
  - [ ] Sub-Task 7.5: Global API Security, Pagination, Throttling & IDOR Tests

---

## ⚠️ STRICT RULES & BOUNDARIES
1. ZERO AI ATTRIBUTION: No `Co-Authored-By`, `Generated with Claude`, or any AI markers in commits, docstrings, or files.
2. NO CODE COMMENTS: Avoid unnecessary `#` comments. Write self-explanatory Python/TypeScript with strict type safety.
3. NO FAKE AI: Classification must be deterministic, multi-signal, and transparent. Do not call or simulate an LLM.
4. STRICT IDOR PROTECTION: Every endpoint must scope queries to `request.user`. No user may see or mutate another user's files, folders, or operations.

---

## Active Task Requirements

### Phase 6: Multi-Signal Classification Engine (`apps/catalog/classification/`)
- Create modular signal extractors:
  - `ExtensionSignal`: maps standard extensions to candidate categories.
  - `MimeSignal`: leverages `filetype` and stdlib `mimetypes` to detect actual content type.
  - `FilenameSignal`: detects keywords/patterns (e.g., `receipt`, `invoice`, `setup`, `test_`, `docker-compose`).
  - `ContextSignal`: directory context clues (e.g. inside `node_modules`, `Downloads/Code`, `DCIM`).
- Evaluator:
  - `classify_file(file_entry: FileEntry | File) -> ClassificationResult`
  - Returns `category_slug`, `confidence` (float 0.0 - 1.0), and `signals_used` (dict).
  - Deterministic evaluation: if signals conflict or confidence < threshold (e.g., 0.5), assign category `unclassified`.
- Celery Task Integration:
  - Wire classification into `scan_folder_task` or run as batch task `classify_unclassified_files_task(folder_id)`.
- Tests (`backend/tests/classification/test_classifier.py`):
  - Test pure extension classification.
  - Test MIME type override when extension is ambiguous or missing.
  - Test unclassifiable files deterministically map to `unclassified` with low confidence.

---

### Phase 7: Complete DRF API Surface (`backend/apps/`)
Standardize all endpoints with DRF ViewSets, `PageNumberPagination` (default 50 items), filtering via `django-filters`, and strict `IsAuthenticated` permissions.

1. **Files API (`apps/catalog/`)**:
   - `GET /api/v1/files/`: List files with filters (`folder_id`, `category`, `extension`, `is_duplicate`, `search`).
   - `GET /api/v1/files/<uuid>/`: File detail with metadata JSONB and duplicate group status.
   - `GET /api/v1/categories/`: List all available categories with file counts.

2. **Rules & Suggestions API (`apps/rules/`, `apps/suggestions/`)**:
   - `GET /api/v1/rules/`, `POST`, `PATCH`, `DELETE`: Rule management with priority ordering.
   - `POST /api/v1/rules/<uuid>/dry_run/`: Return list of file IDs that match rule conditions without changing anything.
   - `GET /api/v1/suggestions/`: List active suggestions (filter by status `pending`).
   - `POST /api/v1/suggestions/<uuid>/accept/`: Transitions suggestion to accepted and prepares an operation plan.
   - `POST /api/v1/suggestions/<uuid>/dismiss/`: Mark suggestion as dismissed.

3. **Operations & Activity API (`apps/operations/`, `apps/activity/`)**:
   - `GET /api/v1/operations/`: List operations with status filter.
   - `GET /api/v1/operations/<uuid>/`: Operation details with item-level ledger (`OperationItem`).
   - `GET /api/v1/activity/`: Read-only audit log feed ordered by `created_at DESC`.

4. **Settings API**:
   - `GET /api/v1/settings/`, `PATCH /api/v1/settings/`: Get and update user preferences (e.g., default conflict policy, auto-scan interval).

5. **Security & IDOR Tests (`backend/tests/api/`)**:
   - Test that User A cannot read or modify User B's folders, files, duplicate groups, or operations.
   - Verify pagination headers and consistent JSON error envelopes.

---

## Phase 6 & Phase 7 Acceptance Gate Checklist
- [ ] Classifier deterministically categorizes files using multiple signals (extension, MIME, patterns).
- [ ] Unknown files fallback to `unclassified` category.
- [ ] All public endpoints (`/api/v1/files/`, `/categories/`, `/rules/`, `/suggestions/`, `/operations/`, `/activity/`, `/settings/`) are live and documented.
- [ ] Querysets are strictly scoped to `request.user` (IDOR tests pass).
- [ ] `pytest backend/tests/` passes with 0 failures.
- [ ] `ruff check backend` passes with 0 errors.
- [ ] ZERO AI attribution tags in any file or commit.