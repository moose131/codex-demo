from __future__ import annotations

import json
from pathlib import Path


class StorageError(Exception):
    """Raised when stored expense data cannot be read or written."""


def default_data_file() -> Path:
    return Path(__file__).resolve().parent.parent / "expenses.json"


def load_expenses(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StorageError(f"Invalid JSON in {path}") from exc
    except OSError as exc:
        raise StorageError(f"Could not read {path}") from exc

    if not isinstance(raw, list):
        raise StorageError(f"Expected a list in {path}")
    return raw


def save_expenses(path: Path, expenses: list[dict]) -> None:
    try:
        path.write_text(json.dumps(expenses, indent=2), encoding="utf-8")
    except OSError as exc:
        raise StorageError(f"Could not write {path}") from exc

