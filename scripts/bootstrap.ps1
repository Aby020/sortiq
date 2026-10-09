#!/usr/bin/env pwsh
# bootstrap.ps1 — Initialize Sortiq development environment

param()

function Confirm-Command($cmd) {
    Write-Host "Running: $cmd"
    Invoke-Expression $cmd
}

# 1. Docker
Write-Host "Checking Docker daemon..."
try {
    docker info > $null 2>&1
    Write-Host "Docker OK. Starting services..."
    docker compose up -d
} catch {
    Write-Warning "Docker not available; skipping container start"
}

# 2. Sync dependencies
Write-Host "Syncing dependencies (uv sync)..."
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv sync
} else {
    pip install -q -e ".[dev]"
}

# 3. Django migrations (using backend package root via PYTHONPATH)
Write-Host "Applying Django migrations..."
$env:DJANGO_SETTINGS_MODULE = "config.settings.base"
$env:PYTHONPATH = "backend"
python manage.py migrate 2>&1 | Out-String | Write-Host

# 4. Bootstrap admin
Write-Host "Bootstrapping admin..."
python manage.py bootstrap_admin 2>&1 | Out-String | Write-Host

Write-Host ""
Write-Host "=== Sortiq Dev URLs ===" -ForegroundColor Cyan
Write-Host "Django control plane : http://localhost:8000"
Write-Host "FastAPI service     : http://localhost:8100"
Write-Host "Health endpoint     : http://localhost:8000/health/"
