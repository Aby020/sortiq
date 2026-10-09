# 01 — Sortiq Product Design

> Working directory: `D:\AbiLabs\Sortiq`
> Scope of this document: **product** — vision, UX, screens, the intelligence
> (classification), the duplicate pipeline, the safe-operations engine, and the
> database/domain model. Delivery architecture is in
> [`02-architecture.md`](02-architecture.md). The build sequence is in
> [`03-roadmap.md`](03-roadmap.md).

---

## 1. Product vision & positioning

**Sortiq is a desktop-first intelligent file management platform.**

One-line pitch: *Sortiq watches your folders, understands what your files are,
keeps a live index, finds duplicates and wasted storage, proposes organization,
and executes it safely — every move recorded, previewed, and undoable.*

It is **not** "FileFlow 2.0". FileFlow is a single-folder, extension-only,
straight-to-disk mover with session-scoped undo. Sortiq is a durable intelligent
platform:

- **Multiple managed folders**, each a registered root with its own scan/watch
  lifecycle.
- **A live index** of everything seen (files, directories, metadata, hashes,
  categories) in PostgreSQL — queries, filtering, and analytics over state, not
  re-walks.
- **Multi-signal classification** (extension + MIME + filename + context + size +
  timestamps + metadata + user rules) with confidence, deterministic by default,
  with a clean seam for optional AI assistance later.
- **A safe operations engine**: preview-by-default, conflict policies,
  persistent operation journal, best-effort rollback with precondition checks,
  crash recovery.
- **Background work** (scans, hashing, analysis, automation) as observable,
  cancellable jobs with real progress.

### Targeted user (persona)

"Alex" is a developer/creator with a home computer and a few scattered folders —
`Downloads`, `Desktop`, a media drive, a code directory. Their pain: files
arrive from many sources; duplicates waste disk; finding anything is guesswork;
organizing by hand is tedious and reorganizing *again* is worse because they
can't undo reliably. Alex wants to press "scan", see clean suggestions, hit
"apply", and know it's reversible and safe.

### Non-goals for v1 (explicit)

- Cloud sync or file *serving* (Sortiq manages the index and moves files; it is
  not a Dropbox).
- Content preview/thumbnails for every media type (a later nicety).
- Multi-device remote management (the architecture permits a home-server
  deployment later; v1 is local-first).
- AI-generated organization as a default — "no fake AI features". The
  architecture has an inference seam; nothing intelligent is mandatory to
  function.

---

## 2. Primary user workflows (happy paths)

1. **Onboard** → tell Sortiq which folders to manage → it scans each, builds the
   index, and lands on the Dashboard.
2. **Understand** → Storage screen shows where space goes (by category, extension,
   folder) and how much is reclaimable from duplicates/large files.
3. **Find** → Explore screen: search, filter (category/type/size/date/folder),
   open a file's metadata.
4. **Dedupe** → Duplicates screen lists groups; user keeps the reference, and
   removal of the rest is prepared as a *previewed operation*.
5. **Organize** → Rules & Suggestions propose moves with reasons and confidence;
   user reviews the diff, edits, then **executes** → a background job moves files
   one-by-one with per-item outcomes.
6. **Audit & undo** → Operations screen lists everything with before/after; any
   recent operation can be rolled back; Activity shows the event feed.
7. **Leave it running** → new files are watched/indexed, suggestions appear,
   automation rules can apply approved patterns automatically.

Every mutation on disk must go through the **operations engine** (byte `0`
principle of this product): no screen ever calls a filesystem mutation directly.

---

## 3. Information architecture & screens

Final v1 screen set (10). Each is a real screen with loading/empty/error states,
keyboard usability, and responsive behavior.

### 3.1 Dashboard
- At-a-glance: number of managed folders, indexed files/dirs, last scan state,
  duplicate bytes, suggestions pending, recent activity.
- Quick actions: add folder, start scan, open suggestions, open duplicates.
- Nothing auto-runs destructively.

### 3.2 Explore (file explorer + search)
- Left: folder tree of the selected managed root *as currently on disk*.
- Main: virtualized file/dir list (name, size, modified, type, category chip,
  duplicate badge, symlink marker). Open, reveal? (v1: copy path), view metadata
  drawer.
- Toolbar: search (name/path), filters (category, extension, size range, date
  range, only duplicates, only unclassified), sort. Export a CSV of the current
  view.
- Careful: this screen reads the *live filesystem* through the backend listing
  service; the index augments the list (category, hash, duplicates, metadata).

### 3.3 Scan Center (folders & scan jobs)
- Managed folders list: path, root stats, watch toggle, last scan summary,
  per-folder actions (Scan now, edit, remove-from-Sortiq).
- Add-folder flow: server-side root picker (drives + path browse) → path
  validation (PathGuard) → scan options (recursive, follow symlinks, hash
  strategy, exclusions) → submit as a job.
- Job list/inbox: live progress (% , stage: walking / indexing / hashing /
  classifying / done), counts (new/changed/removed/errors/skipped), Cancel.

### 3.4 Duplicates
- Groups table: size, count, total reclaimable bytes, members expandable with
  full paths.
- Group actions → resolve dialog: choose keeper; action for the rest = move to
  Sortiq quarantine (default) or delete; prepares an **operation** (previewed,
  not executed).
- Filtering by folder, size thresholds, status.

### 3.5 Storage Analytics
- Overview tiles: total managed, index growth, duplicate overhead, largest top
  categories/extensions, largest files.
- Charts: storage by category, by folder, by time bucket (created/modified);
  "top N large files"; empty-folder list.
- All queries run against the index/analytics views; heavy aggregations are
  background jobs that materialize snapshots (fast UI).

### 3.6 Suggestions
- Proposed organization actions from rules + heuristics: file → category folder
  / rename / tag, each with reason and confidence.
- Bulk-select → "Plan operation" → opens the Operation preview.
- Dismiss/accept; resolved suggestions never reappear.

### 3.7 Rules & Automation
- Rule list: name, priority, enabled, condition summary, action summary.
- Rule editor: condition builder (matchers: extension, mime, name pattern,
  size, date, folder, is-duplicate, custom predicate) + action (move to
  category, rename pattern, tag) + when (manual / on-scan / scheduled).
- "Dry-run match" produces matching files; "Plan apply" is the only way an
  automation touches disk.
- Priority-ordered evaluation; the first matching rule with a definitive action
  wins, others scored for suggestion purposes.

### 3.8 Operations
- History table (type, scope, created, status, outcome summary, rollback badge).
- Operation detail: per-item ledger (source → target, before/after snapshots,
  outcome, error code).
- Actions: Execute a planned/previewed op, Cancel a running one, **Rollback** a
  completed one (with safety warnings when preconditions fail).

### 3.9 Activity
- Event feed (scans finished, duplicates found, suggestions created, operations
  executed/rolled back, rules changed, errors).
- Filterable/summarized; security-relevant events always included.

### 3.10 Settings
- Profile, appearance (theme from design tokens), region/locale,
  storage/hashing defaults (scan strategy, hash levels, quarantine location),
  privacy (log/retention windows), about.
- No settings affect safety invariants (protected paths are never user-disableable).

### Screen cut list (from Task.md suggestions)

Kept: Dashboard, File Explorer (Explore), Folder Management → Scan Center,
Duplicate Manager, Storage Analytics, Organization Suggestions, Rules/Automation,
Operation Preview → Operations, Operation History → Operations, Activity Center,
Settings.
- **Operation Preview** merged into Operations (preview is a first-class step of
  any operation flow, not a separate screen).

---

## 4. File Intelligence — multi-signal classification

Not extension-only. A **Classifier service** scores each file against the
category taxonomy using pluggable, weighted, deterministic signals. Every signal
is a small, pure, unit-tested function; the pipeline runs in the index job.

### 4.1 Signals (v1)

| Signal | Source | Cost | Weight (default) |
| --- | --- | --- | --- |
| Extension | filename | trivial | high |
| MIME type | content sniff + extension cross-check | low (head read) | high |
| Filename | token/n-gram/keyword patterns | trivial | medium |
| Directory context | parent dir names ("music", "backups") | trivial | medium |
| Size | stat | trivial | low |
| Timestamps | stat (age buckets) | trivial | low |
| Metadata (optional) | EXIF/media/header extraction | medium | low–med |
| User rules | priority-ordered matchers | trivial | **highest, overrides** |

Logic: (a) evaluate **user rules first** — a matching rule is authoritative;
(b) otherwise combine the signal scores into a **confidence-weighted category
vector**; (c) if top confidence is below a threshold → leave **Unclassified**
(rather than guessing). The output is `{category, confidence, signals[]}`.

### 4.2 Design properties

- **Deterministic by default**: same file → same result, given same rule
  version. Each category assignment records `category_signals` and the
  `rule_version`/signal-spec version so reclassification is easy when rules or
  taxonomy change.
- **Pluggable & testable**: signals are registered functions (`ExtensionSignal`,
  `MimeSignal`, `FilenameSignal`, …). Adding one is adding a module + a weight,
  not touching the pipeline.
- **AI seam (no fake AI)**: an `InferenceSignal` *interface* exists but is not
  enabled by default. When enabled later it must follow the AI/NLP standard:
  provider behind a service, structured validated output, pinned model +
  prompt version, evals, timeouts/retries/caching. AI is never required for
  basic operation.
- **Perf**: classification runs on the hashing/scan worker pipeline; results are
  cached on the file row and invalidated when a file changes or rule version
  bumps (no AI call per re-scan — reclassify only delta files).

### 4.3 Category taxonomy

- Data-driven (`categories` table), seeded with a sane taxonomy
  (Images, Documents, Videos, Music, Archives, Programs, Development,
  Shortcuts, Others; each with display tokens/colors). Slugs are stable keys;
  categories are extendable via the API, not code edits.

---

## 5. Duplicate detection pipeline

Goal: find exact duplicates (same content) with minimal wasted I/O, correctness
under races, and honest per-file error handling. **Never hash every file from
byte zero without a better strategy.**

### 5.1 Stages

1. **Candidate filter — file size.** Group indexed files by `(size_bytes)`
   among the target scope. Singletons are discarded immediately (zero reads).
2. **Metadata shortcut.** For files whose stored `sha256` exists and whose
   `(size, mtime_ns, inode_identity)` fingerprint is unchanged since it was
   produced, reuse the stored hash (no re-read). Changed/new files proceed.
3. **Partial hash.** Read the first 64 KiB **and** last 64 KiB of each
   same-size candidate (streaming, bounded memory); compute a fingerprint.
   Groups whose partial fingerprints differ are dismissed.
4. **Full cryptographic hash.** SHA-256, streamed in 1 MiB chunks with an
   `is_cancelled` callback, only for remaining candidate groups.
5. **Group assembly.** Files sharing a full hash (excluding hard-link aliases
   and `follow_symlinks=false` symlinks — policy) form a `duplicate_group`.

Additional constraints applied at group time: files smaller than a configurable
threshold (default 0 bytes; a sane floor may be chosen) can be excluded; groups
spanning only hard links are reported but not flagged as "reclaimable".

### 5.2 Edge-case handling (from the Task list)

| Case | Behavior |
| --- | --- |
| Large files | Streamed partial-then-full; never full bytes unless needed |
| Permissions / unreadable | Record `hash_error` per file; mark job skipped-count; retry on next incremental run |
| Symlinks | Not followed by default; link recorded with `is_symlink` + target; policy flag to include/follow |
| Files changing during scan | Stat before and after each read (size/mtime/inode). If changed mid-read → mark "changed during scan", skip grouping this run, record; the watcher/incremental run re-checks |
| Sparse files | `SEEK_DATA/SEEK_HOLE`-aware hashing when the platform supports it; otherwise read only declared extents |
| Hard links | Fingerprint includes inode identity so aliases are detected; grouped distinctly (reclaimable vs not) |
| Race with movement | If a file disappears mid-read → record error code `missing_during_read`, continue |
| Hashing cache | Persisted on the `files` row (`sha256`, `partial_hash`, `hash_stage`, `hash_verified_at`, fingerprint); invalidated on change events |

### 5.3 Outputs

- `duplicate_groups` + members; each member flagged `kept`/`reference`.
- Reclaimable-bytes analytics (`analysis` endpoint): `sum(size * (count-1))` per
  scope.
- Operations for resolution are **proposals**, never auto-executed.

---

## 6. Safe operations & rollback engine

This is the product's safety-critical core. Design principles:

1. Every disk mutation is an **Operation** with a plan, a persistent journal, and
   a recorded outcome. `enum.verify`: **no screen touches filesystem mutation
   directly**.
2. **Preview is normative**: the plan generated for preview is the *same*
   artifact executed later (validated again at execution time). If disk state
   changed between preview and execute, items are re-verified and conflicts
   re-evaluated.
3. **Stat-before-act**: each item is re-stated immediately before acting; a file
   that changed identity (size/mtime/inode) since planning is skipped and
   reported, never acted on blindly.
4. **Nothing destructive is unrecoverable by default**: deletes default to
   **quarantine** (move into a managed `.sortiq` quarantine folder on the same
   volume). True `unlink` is an explicit, higher-friction choice.

### 6.1 Operation lifecycle

`planned → executing → completed | partially_completed | failed | cancelled | rolled_back`

- **Plan**: entity list of `OperationItem`s from scope + rules/filters; runs
  conflict detection; produces preview (UI) or a stored plan.
- **Conflict detection**:
  - target exists → policy `skip | rename | overwrite` (global or per-item);
  - two items planning the same target (collision);
  - move into self-subtree (copy would nest) → reject item;
  - overlapping concurrent operations on same paths → refuse to start second one.
- **Journal (WAL-style)**: before each physical action, an `operation_items` row
  is written with `outcome=pending` plus the reverse-action descriptor
  (`rollback_state`). On restart, any `pending` item is resolved (re-verify →
  complete or rollback) — the journal is the source of truth for recovery.
- **Execution**: per item — verify preconditions → act (`move | copy | rename |
  delete(touch quarantine) | mkdir`) → stat post-state → record outcome. Partial
  failures accumulate in the item ledger and are rolled into an honest summary.
- **Cancellation**: cooperative flag checked between items and inside long hashes;
  in-flight item completes atomically; remaining items recorded `skipped_cancel`;
  operation marked `cancelled`.
- **Rollback**: for `completed`/`partially_completed` operations, replay
  `rollback_state` in reverse, but **only when preconditions hold**: source file
  still exists with unchanged fingerprint, target slot is free (or policy
  `overwrite` is explicitly chosen), and no newer operation has touched the item.
  Conflicts → skip that item + report. Rollback creates *its own* operation
  record (an audit event), it never mutates history in place.

### 6.2 Path safety (PathGuard)

Centralized, test-only-through-public-API validation:

- **Canonicalize**: resolve to a real absolute path (Windows: `1-`-letter drive +
  normalized separators; Python `Path.resolve(strict=False)`), reject NUL /
  control characters / path > platform max.
- **Allowlist containment**: mutations only under registered managed roots
  (`folder.root_path`) and per-operation declared subscope.
- **Deny-list**: drive roots, system dirs (%SystemRoot%, Program Files,
  C:\Users\... home), the app's own data/quarantine dirs (managed separately),
  and any path whose parent chain touches them.
- **Symlink / junction policy**: `follow_symlinks=false` for scanning; for
  mutation, a symlink's *link itself* may be moved but its target is never
  dereferenced; a path whose resolved target escapes the allowlist is rejected.
- **Recursion guard**: never organize a folder into itself or into its own
  descendants; refuse rules targeting the root of a managed folder's parent of
  another managed folder when it would cross-manage.
- Return typed rejection reasons (permissions, traversal, contains_denied…)
  instead of opaque failures.

### 6.3 Filesystem testing guard

The engine (and its tests) operate **only** inside `tempfile`-managed trees
created by tests — the product never touches real user folders unexpectedly. A
`TreeBuilder` test harness assembles directory trees as fixtures with real
files/symlinks/junctions; tests assert on the prepared tree only.

---

## 7. Database & domain model (PostgreSQL, Django-owned schema)

Follows `standards/database`: 3NF, constraints at the DB, `snake_case` plural
tables, `id` PK, `FK <table>_id`, booleans `is_*`/`has_*`, indexes on query
patterns, `created_at`/`updated_at`. **Postgres is the only source of truth for
app state**; Redis holds only ephemeral (queue, cache, job progress).

### 7.1 Entities

| Table | Purpose | Key fields |
| --- | --- | --- |
| `users` | Django auth (email/password) | standard Django fields |
| `folders` | Managed roots | `user_id`, `root_path` (normalized), `name`, `is_active`, `watch_enabled`, `recursive_scan`, `follow_symlinks`, `last_scan_completed_at` |
| `categories` | Taxonomy (seeded, extendable) | `slug` (unique), `name`, `description`, `is_system`, `sort_order`, `color_token` |
| `files` | Live index of every seen file/dir | `folder_id`, `relative_path`, `path_lower`, `name`, `extension`, `is_dir`, `parent_dir`, `size_bytes`, `mtime_ns`, `ctime_ns`, `inode_identity`, `is_symlink`, `symlink_target`, `mime_type`, `sha256`, `partial_hash`, `hash_stage`, `hash_error`, `hash_verified_at`, `category_id`, `category_confidence`, `category_signals`, `duplicate_group_id`, `first_seen_at`, `last_seen_at`, `last_scanned_at`, `deleted_at` |
| `file_metadata` | Extracted metadata (1:1) | `file_id`, `payload` (JSONB), `extractor_version`, `extracted_at` |
| `duplicate_groups` | Exact-dup groups | `size_bytes`, `algorithm`, `member_count` |
| `duplicate_group_members` | Membership | `group_id`, `file_id`, `is_reference`, `kept` |
| `organization_rules` | User rules | `user_id`, `name`, `priority`, `enabled`, `conditions` (JSONB predicate), `action` (JSONB), `version` |
| `organization_suggestions` | Proposed actions | `user_id`, `folder_id?`, `file_id?`, `rule_id?`, `suggested_action` (JSONB), `reason`, `confidence`, `status` (pending/accepted/dismissed/superseded) |
| `operations` | Operation header | UUID `id`, `type`, `scope` (JSONB), `policy` (JSONB), `status`, `summary` (JSONB), `rollback_available`, `job_id?` |
| `operation_items` | Per-action ledger (the journal) | `operation_id`, `sequence`, `kind` (move/copy/rename/delete/mkdir), `source_path`, `target_path`, `source_snapshot` (JSONB), `target_snapshot` (JSONB), `outcome`, `after_snapshot`, `error_code`, `error_message`, `rollback_state`, `executed_at` |
| `jobs` | All background jobs (scan, duplicate, classify, analyze, automate, organize) | `kind`, `folder_id?`, `state` (PENDING/RUNNING/COMPLETED/FAILED/CANCELLED), `progress_pct`, `progress_stage`, `counts` (JSONB), `params` (JSONB), `error` (JSONB), `celery_task_id`, `requested_cancel`, `heartbeat_at` |
| `activities` | Event feed | `user_id?`, `actor`, `job_id?`, `event_type`, `payload` (JSONB), `created_at` |
| `settings` / `user_preferences` | Key-value store | `key`, `value` (JSONB), `is_global` |

### 7.2 Relationships

- `users 1—N folders`, `users 1—N organization_rules`, `users 1—N suggestions`
- `folders 1—N files` (a file belongs to exactly one managed root; `relative_path`
  is unique within it)
- `files 1—0..1 file_metadata`, `files 0..1—N duplicate_group_members` (via
  `duplicate_group_id` on the member join)
- `operations 1—N operation_items`, `operations 0..1—1 jobs`
- `jobs 0..1—1 folder` (scans bound to a root)
- `files 0..1—1 categories`, `files 0..N suggestions`, `files 0..N operation_items`
  (referenced via snapshot paths; FKs guarded)
- `activities.job_id → jobs` (weak, nullable)

### 7.3 Key constraints & indexes

- `UNIQUE (folder_id, path_lower)` **partial** (`WHERE deleted_at IS NULL`) —
  Windows is case-insensitive; `path_lower` (citext-style, lowercased in
  Python/DB) enforces one live row per path spelling.
- `CHECK`: `size_bytes >= 0`; `progress_pct BETWEEN 0 AND 1`; hash consistency —
  `NOT (sha256 IS NOT NULL AND hash_error IS NOT NULL)`.
- `CHECK` on `hash_stage` ∈ `{0,1,2}`; on `operation_items.outcome` ∈ enumerated
  set; on `operations.status` ∈ enumerated set.
- Duplicate membership: `UNIQUE (group_id, file_id)`;
  `file.duplicate_group_id` kept on `files` for quick badge queries.
- Indexes (match query patterns):
  - `ix_files_folder_path (folder_id, path_lower)`
  - `ix_files_folder_deleted (folder_id, deleted_at)`
  - `ix_files_category (category_id)`, `ix_files_extension (extension)`
  - `ix_files_size (size_bytes)`
  - `ix_files_sha256 (sha256)` **partial** `WHERE sha256 IS NOT NULL`
  - `ix_files_mtime (mtime_ns)`
  - `ix_files_duplicate_group (duplicate_group_id)`
  - `ix_op_items_operation (operation_id, sequence)`
  - `ix_operations_status (status)`, `ix_operations_created (created_at)`
  - `ix_jobs_state (state)`, `ix_jobs_kind_created (kind, created_at)`
  - `ix_activities_created (created_at)`
  - `ix_suggestions_status (status)`
- FKs on every `*_id` (standard `ix_` suffix omitted here for brevity where the
  column is a lead of a composite above).

### 7.4 Lifecycle & retention

| Data | Lifecycle |
| --- | --- |
| `files` | Soft-deleted (`deleted_at`) when a scan finds a path gone; purged after `N` days (default 30) unless referenced by an open operation/suggestion. Re-created on reappearance. |
| `file_metadata` | Lives/dies with its file |
| `file_hashes` | On `files`; invalidated on file change events; re-hash lazily |
| `operations` + `operation_items` | **Never pruned** — permanent audit trail |
| `activities` | Pruned after `N` days (default 90), summarized first |
| `organization_suggestions` | Resolved ones pruned after `N` days (default 30) |
| `jobs` | Completed ones pruned after `N` days (default 30), keeping summary |

---

## 8. UX principles (summary)

- **Preview by default is the flagship interaction.** Every destructive or
  mass action shows the exact diff first.
- **State, never silence**: loading skeletons, progress stages, empty states
  with a next action, error states with a recovery path.
- **Destructive protection**: quarantine by default; a true-delete requires an
  explicit higher-friction confirmation.
- **Keyboard-first + a11y**: full focus management, keyboard nav for lists and
  dialogs, semantic HTML, `prefers-reduced-motion` respected, token-driven
  themes (light/dark).
- **Progress honesty**: real job stages and percent from the worker; cancellation
  always available on long jobs.

---

*Next: [`02-architecture.md`](02-architecture.md) — system architecture, service
boundaries, background jobs, filesystem integration, API, security, testing,
dev/deploy, risks, and the decisions needing approval.*