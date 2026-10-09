# SORTIQ — Task.md

## Project Metadata
- **Project Name:** Sortiq (Intelligent Desktop File Management Platform)
- **Directory:** `D:\Abilabs\Sortiq`
- **Reference Project:** `D:\Abilabs\FileFlow-Reference` (READ-ONLY, DO NOT TOUCH)
- **Current Phase:** Phase 1 — Repository Foundation, Dev Environment & Authentication Skeleton
- **Active Task:** Task 1 — Repository Foundation & Core Service Skeletons

---

## ⚠️ Phase 1 Critical Scope Boundaries
**DO NOT IMPLEMENT:**
- Duplicate detection, staged hashing, or partial hash pipelines.
- File organization heuristics, suggestions, or user-defined rule engines.
- Filesystem mutation operations (move, rename, delete, quarantine) or rollback journals.
- Advanced storage analytics or full React views.
- Any AI/LLM integration.
- No business logic leakage from Phases 2–14.

---

## Work Execution Protocol
1. Work sequentially through Sub-Tasks 1.1 to 1.8.
2. After completing each sub-task, run linting and tests to verify stability.
3. Pause for verification after each sub-task before proceeding to the next.
4. Keep inline `#` comments to a strict minimum (only for non-obvious edge cases).
5. All paths, scripts, and commands must be native Windows/PowerShell compatible.

---

## Task 1 Breakdown

### Sub-Task 1.1: Git Workspace & Layout
- [ ] Initialize an independent Git repository in `D:\Abilabs\Sortiq` (no legacy FileFlow commits).
- [ ] Build the canonical directory structure:
  ```text
  Sortiq/
  ├── backend/
  │   ├── apps/
  │   │   ├── __init__.py
  │   │   └── authentication/
  │   ├── config/
  │   │   ├── __init__.py
  │   │   ├── asgi.py
  │   │   ├── settings/
  │   │   │   ├── __init__.py
  │   │   │   ├── base.py
  │   │   │   ├── development.py
  │   │   │   └── production.py
  │   │   ├── urls.py
  │   │   └── wsgi.py
  │   ├── service/
  │   │   ├── __init__.py
  │   │   └── main.py
  │   └── sortiq_fs/
  │       └── __init__.py
  ├── frontend/
  ├── scripts/
  ├── docs/
  │   └── planning/
  ├── .env.example
  ├── .gitignore
  ├── docker-compose.yml
  └── pyproject.toml