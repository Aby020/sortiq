# SORTIQ — Active Sprint: Phases 12, 13, 14 & Final Project Release (v1.0.0)

## Status: IN PROGRESS
- [x] Phase 1: Repository Foundation, Dev Environment & Auth Skeleton
- [x] Phase 2: Database Domain Model & Migrations
- [x] Phase 3: Filesystem Engine (`sortiq_fs`)
- [x] Phase 4: Folder Registration, Scanning Pipeline & React Scan Center
- [x] Phase 5: Staged Duplicate Detection Engine, Resolution & UI
- [x] Phase 6: Multi-Signal Classification Engine
- [x] Phase 7: Complete DRF API Surface & Security Hardening
- [x] Phase 8: Background Services & FastAPI Internal Execution Plane
- [x] Phase 9: Safe Operations Engine (WAL Journal, Stat-Before-Act, Rollback)
- [x] Phase 10: Suggestions, Rules & Automation Engine
- [x] Phase 11: Comprehensive UI/UX Polish (10 Approved Screens)
- [/] Phase 12: Security Hardening & Observability Review
  - [ ] Sub-Task 12.1: Path Adversarial & Traversal Security Audit (`backend/tests/security/`)
  - [ ] Sub-Task 12.2: Secret Leak & Dependency Audit Check
  - [ ] Sub-Task 12.3: Structured Request Correlation & Observability (`structlog`)
- [/] Phase 13: Comprehensive QA & Invariant Verification
  - [ ] Sub-Task 13.1: Windows Path Semantics & Long Path Safety Verification
  - [ ] Sub-Task 13.2: Concurrent Scan/Modification Collision Invariant Tests
  - [ ] Sub-Task 13.3: Operations Journal Integrity & State Machine Invariants
- [/] Phase 14: Production Packaging, Documentation & Release Sign-Off
  - [ ] Sub-Task 14.1: Production Dockerfile & Multi-Stage Production Build
  - [ ] Sub-Task 14.2: Comprehensive Architectural & Technical Documentation (`docs/` & `README.md`)
        - `README.md`: High-level vision, architecture diagram, quickstart, engineering highlights.
        - `docs/ARCHITECTURE.md`: Dual-plane Django/FastAPI model, Operations WAL engine, state machines.
        - `docs/SECURITY.md`: PathGuard containment, stat-before-act, IDOR matrix, secret isolation.
        - `docs/API.md`: Public REST API spec and internal service contract.
  - [ ] Sub-Task 14.3: Final Release Tag & Working Tree Verification (v1.0.0)

---

## ⚠️ STRICT RULES & BOUNDARIES
1. ZERO AI ATTRIBUTION: No `Co-Authored-By`, `Generated with Claude`, or any AI markers in commits, docstrings, or files.
2. NO CODE COMMENTS: Avoid unnecessary `#` comments. Write self-documenting code.
3. ABSOLUTE PORTFOLIO QUALITY: Documentation must be technically rigorous, explaining real engineering tradeoffs (Django vs FastAPI, WAL journaling, staged hashing, Windows reparse points).

---

## Active Task Requirements

### Phase 12: Security Hardening & Observability
- **Security Audit Test Suite (`backend/tests/security/test_security_audit.py`)**:
  - Path traversal injection: `../../Windows/System32`, `C:..\secret.txt`, NUL byte injection (`file.txt\0.pdf`), reserved devices (`COM1`, `LPT1`).
  - Cross-user folder access: Ensure User B cannot read or trigger scans on User A's folder.
  - Token verification: Verify FastAPI `/internal/` rejects spoofed or missing service tokens.
- **Correlation ID Middleware**:
  - Ensure every incoming request attaches an `X-Request-ID` UUID to both response headers and `structlog` context.

---

### Phase 13: QA, Windows Path Semantics & Invariants
- **Windows Path Edge-Case Suite (`backend/tests/fs/test_windows_paths.py`)**:
  - Test drive letter normalization (`c:\` vs `C:/`).
  - Test mixed slash normalization (`D:\Folder/subfolder\file.txt`).
  - Test case insensitivity handling on Windows paths.
- **Journal State Machine Verification**:
  - Validate that operation states cannot transition illegally (e.g. `completed` -> `executing`).
  - Ensure rollback operations strictly generate independent audit records.

---

### Phase 14: Documentation & Production Packaging
1. **Production Docker Configuration**:
   - `Dockerfile.backend`: Multi-stage build for Django + Celery.
   - `Dockerfile.service`: Lean async runtime for FastAPI.
   - `Dockerfile.frontend`: Multi-stage build serving static assets via Nginx.
2. **Technical Documentation**:
   - `README.md`: Flagship project presentation with ASCII architecture diagram, tech stack breakdown, and quickstart commands (`bootstrap.ps1`, `dev.ps1`).
   - `docs/ARCHITECTURE.md`: Deep dive into control plane vs execution plane, staged deduplication pipeline, WAL state machine, and PathGuard containment.
   - `docs/SECURITY.md`: Defensive filesystem engineering, containment proofs, stat-before-act invariants, authentication, and authorization models.
   - `docs/API.md`: Standardized endpoint documentation with request/response envelopes.
3. **Repository Cleanliness Check**:
   - Ensure `git status` is clean, all files pass `ruff`, frontend builds cleanly (`vite build`), and no credential leaks exist.

---

## Final Acceptance Gate (v1.0.0 Ready)
- [ ] All security adversarial tests pass.
- [ ] Windows path normalization tests pass.
- [ ] Complete documentation package (`README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `API.md`) is written and formatted.
- [ ] Production Dockerfiles are present and valid.
- [ ] `ruff check backend` passes with 0 errors.
- [ ] `npx vite build` in `frontend/` succeeds cleanly.
- [ ] `git log` and codebase are 100% free of AI attribution markers.