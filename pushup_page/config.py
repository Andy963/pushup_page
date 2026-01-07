from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = REPO_ROOT / "assets"
DB_PATH = REPO_ROOT / "data.db"
CSV_PATH = REPO_ROOT / "pushup_data.csv"

# Backwards-compatible alias used throughout the project.
SQL_FILE = str(DB_PATH)
