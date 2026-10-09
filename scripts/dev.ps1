#!/usr/bin/env pwsh
# dev.ps1 — Start Sortiq development servers (Django :8000, FastAPI :8100, Celery worker)

$jobs = @()

function Start-Django() {
    Write-Host "Starting Django on :8000..."
    $env:DJANGO_SETTINGS_MODULE = "config.settings.base"
    $env:PYTHONPATH = "backend"
    python manage.py runserver 0.0.0.0:8000
}

function Start-FastAPI() {
    Write-Host "Starting FastAPI on :8100..."
    uvicorn service.main:app --host 0.0.0.0 --port 8100 --reload --app-dir backend
}

function Start-Celery() {
    Write-Host "Starting Celery worker..."
    $env:DJANGO_SETTINGS_MODULE = "config.settings.base"
    $env:PYTHONPATH = "backend"
    celery -A config worker --loglevel=info
}

Write-Host "Launching Sortiq dev stack..."
$jobs += Start-Job -ScriptBlock ${function:Start-Django}
$jobs += Start-Job -ScriptBlock ${function:Start-FastAPI}
$jobs += Start-Job -ScriptBlock ${function:Start-Celery}

Write-Host ""
Write-Host "Django  -> http://localhost:8000"
Write-Host "FastAPI -> http://localhost:8100"
Write-Host "Celery  -> worker running"
Write-Host ""
Write-Host "Press Ctrl+C to stop all jobs"

try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($jobs.State -contains "Failed") {
            Write-Warning "A job failed. Stopping..."
            break
        }
    }
} catch {
    Write-Host "Shutting down jobs..."
}

$jobs | Stop-Job
$jobs | Receive-Job
