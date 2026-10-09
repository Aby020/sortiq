#!/usr/bin/env pwsh
# lint.ps1 — Run ruff + optional mypy

Write-Host "=== Ruff check ==="
uv run ruff check backend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Ruff format check ==="
uv run ruff format --check backend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (Get-Command mypy -ErrorAction SilentlyContinue) {
    Write-Host "`n=== mypy ==="
    uv run mypy backend
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Warning "mypy not installed; skipping"
}

Write-Host "`nLint clean."
