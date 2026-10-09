# Sortiq Security Audit — 20-Point Review

Date: 2026-10-09
Status: Patches applied (Rules 11, 14, 18 verified)
Author: Abi Thomas <abithomas520@gmail.com>

| Rule | Severity | File | Finding | Status |
|---|---|---|---|---|
| 11 — Rate Limit | Critical | config/settings/base.py | Added `DEFAULT_THROTTLE_CLASSES` / `DEFAULT_THROTTLE_RATES` | **PATCHED** |
| 14 — SQL Injection | High | apps/authentication/views.py | `cursor.execute("SELECT %s", (1,))` parameterized | **PATCHED** |
| 18 — DEBUG Default | Medium | config/settings/development.py | `DEBUG = env.bool("DEBUG", default=False)` | **PATCHED** |
| 7 — IDOR | Low | apps/*/viewsets/ | All `get_queryset()` scoped by `request.user` | Verified |
| 2 — Secrets / .gitignore | Low | .gitignore | `.env*`, `*.pem`, `db.sqlite3` excluded | Verified |
| 13 — DRF Serializers | Low | apps/*/serializers/ | ModelSerializers on all bounded contexts | Verified |
| 15 — XSS | Low | frontend/src/ | No `dangerouslySetInnerHTML` / raw HTML | Verified |
| 16 — Upload / Quarantine | Low | sortiq_fs/quarantine.py | PathGuard + filetype MIME + never `unlink` | Verified |
