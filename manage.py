#!/usr/bin/env python
"""Django management entrypoint for the Sortiq control plane."""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()