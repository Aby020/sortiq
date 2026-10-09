# Sortiq

Intelligent Desktop File Management Platform — a modern, local-first tool for scanning, analyzing, and managing file systems on your computer.

## Quick Start (Phase 1 setup only)

### Requirements
- Python 3.11+
- PostgreSQL 14+ (Docker or native)
- Redis 7+ (Docker or native)
- Docker (optional, for database services)

### Installation (backend only)
```bash
# Clone this repo
cd Sortiq

# Create & activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Configure environment
dcp .env.example .env  # or copy/paste values manually

# Run migrations and create superuser
python manage.py migrate
python manage.py createsuperuser

# Launch backend services
python manage.py runserver 0.0.0.0:8000

# (Optional) Start PostgreSQL/Redis via Docker
docker-compose up -d
```

## Repository Structure

Sortiq is organized into:
- **backend/**: Django control plane (DRF, API) and Python file system engine (sortiq_fs).
- **frontend/**: React SPA (Vite) for the UI.
- **scripts/**: PowerShell/CLI helpers for local dev, lint, test, and Docker operations.
- **docs/planning/**: Product & architecture planning documents.

## Features (Phase 1 done)

The repository includes:
- A clean Python project layout with Django, FastAPI, Celery, and Redis.
- Minimal authentication skeleton and file system engine stubs.
- Configuration scaffolding (`.env.example`, `docker-compose.yml`).
- Linting (ruff), testing (pytest), and linting configuration.

## Project Workflow

See the [Task.md](Task.md) in the root for detailed Phase 1 boundaries and tasks.

## Contributing

Follow the existing code style and keep changes small and focused. See the style guide in the project for conventions.

## License

MIT
