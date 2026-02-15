from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    data_file = tmp_path / "expenses.json"
    env = {**os.environ, "EXPENSE_TRACKER_FILE": str(data_file)}
    return subprocess.run(
        [sys.executable, "-m", "expense_tracker", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).resolve().parents[1],
        check=False,
    )


def test_add_list_total_round_trip(tmp_path: Path) -> None:
    add = run_cli(tmp_path, "add", "12.50", "food", "lunch")
    assert add.returncode == 0
    assert "Added: $12.50 | food | lunch" in add.stdout

    list_result = run_cli(tmp_path, "list")
    assert list_result.returncode == 0
    assert "1. $12.50 | food | lunch" in list_result.stdout

    total_result = run_cli(tmp_path, "total")
    assert total_result.returncode == 0
    assert "Total: $12.50" in total_result.stdout


def test_optional_note_defaults_to_dash_in_list(tmp_path: Path) -> None:
    add = run_cli(tmp_path, "add", "7", "transport")
    assert add.returncode == 0

    list_result = run_cli(tmp_path, "list")
    assert list_result.returncode == 0
    assert "1. $7.00 | transport | -" in list_result.stdout


def test_empty_state_commands(tmp_path: Path) -> None:
    list_result = run_cli(tmp_path, "list")
    assert list_result.returncode == 0
    assert "No expenses recorded." in list_result.stdout

    total_result = run_cli(tmp_path, "total")
    assert total_result.returncode == 0
    assert "Total: $0.00" in total_result.stdout


def test_add_rejects_non_positive_amount(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "add", "0", "misc")
    assert result.returncode != 0
    assert "amount must be greater than 0" in result.stderr


def test_invalid_json_file_returns_error(tmp_path: Path) -> None:
    data_file = tmp_path / "expenses.json"
    data_file.write_text("{this is not valid json", encoding="utf-8")
    env = {**os.environ, "EXPENSE_TRACKER_FILE": str(data_file)}
    result = subprocess.run(
        [sys.executable, "-m", "expense_tracker", "list"],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).resolve().parents[1],
        check=False,
    )
    assert result.returncode == 1
    assert "Invalid JSON" in result.stderr


def test_add_persists_to_json_file(tmp_path: Path) -> None:
    run_cli(tmp_path, "add", "3.25", "coffee", "latte")
    stored = json.loads((tmp_path / "expenses.json").read_text(encoding="utf-8"))
    assert stored == [{"amount": 3.25, "category": "coffee", "note": "latte"}]

