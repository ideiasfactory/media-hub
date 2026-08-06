"""Frontend assets: Jinja templates and static files."""

from pathlib import Path

FRONTEND_ROOT = Path(__file__).resolve().parent
STATIC_DIR = FRONTEND_ROOT / "static"
TEMPLATES_DIR = FRONTEND_ROOT / "templates"
