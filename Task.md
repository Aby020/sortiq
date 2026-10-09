# SORTIQ — Active Sprint: Sub-Tasks 1.7 & 1.8 + Phase 1 Gate Verification

## Status: IN PROGRESS
- [x] Sub-Task 1.1: Git Workspace & Layout
- [x] Sub-Task 1.2: Tooling & pyproject.toml Baseline
- [x] Sub-Task 1.3: Django Settings & Environment Setup
- [x] Sub-Task 1.4: Django Control Plane & Authentication App
- [x] Sub-Task 1.5: FastAPI Service Skeleton (`backend/service/`)
- [x] Sub-Task 1.6: Developer PowerShell Scripts (`scripts/`)
- [/] Sub-Task 1.7: CI/CD Pipeline (`.github/workflows/ci.yml`)
- [/] Sub-Task 1.8: Frontend Workspace Setup (`frontend/`)
- [/] Phase 1 Acceptance Gate Validation

---

## Active Task Requirements

### Sub-Task 1.7: CI/CD Pipeline (`.github/workflows/ci.yml`)
- Create GitHub Actions workflow triggered on `push` and `pull_request` against `main`.
- Matrix test strategy:
  - OS: `ubuntu-latest` and `windows-latest`
  - Python: `3.11`
- Pipeline Steps:
  - Checkout repository.
  - Install `uv`.
  - Install dependencies via `uv sync --all-extras`.
  - Run linting: `uv run ruff check backend` and `uv run ruff format --check backend`.
  - Run type checking: `uv run mypy backend` (disallowing untyped definitions).
  - Run test suite: `uv run pytest backend`.

### Sub-Task 1.8: Frontend Workspace Setup (`frontend/`)
- Initialize Vite + React + TypeScript in `frontend/`.
- Configure Tailwind CSS (`tailwind.config.ts`, `postcss.config.js`).
- Include `framer-motion` (Motion) for future transitions/animations.
- Create directory structure:
  ```text
  frontend/src/
  ├── assets/
  ├── components/
  │   └── ui/
  ├── lib/
  │   └── api.ts       # Axios/fetch client targeting localhost:8000 and localhost:8100
  ├── types/
  ├── App.tsx
  └── main.tsx