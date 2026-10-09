#!/usr/bin/env pwsh
# test.ps1 — Run pytest with clean reporting

$env:DJANGO_SETTINGS_MODULE = "config.settings.base"
$env:PYTHONPATH = "backend"

uv run pytest backend `
    --verbose `
    --tb=short `
    --strict-markers

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nAll tests passed."
