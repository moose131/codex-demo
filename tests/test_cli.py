from __future__ import annotations

import csv
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
    assert len(stored) == 1
    assert stored[0]["amount"] == 3.25
    assert stored[0]["category"] == "coffee"
    assert stored[0]["note"] == "latte"
    assert isinstance(stored[0]["time"], str)
    assert stored[0]["time"]


def test_export_writes_csv_with_expected_columns(tmp_path: Path) -> None:
    run_cli(tmp_path, "add", "12.5", "food", "lunch")
    run_cli(tmp_path, "add", "8", "transport")

    csv_file = tmp_path / "out.csv"
    result = run_cli(tmp_path, "export", str(csv_file))
    assert result.returncode == 0
    assert f"Exported 2 expense(s) to {csv_file}" in result.stdout

    with csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["time", "amount", "category", "note"]
    assert rows[1][1:] == ["12.5", "food", "lunch"]
    assert rows[2][1:] == ["8.0", "transport", ""]
    assert rows[1][0]
    assert rows[2][0]


def test_export_empty_data_writes_header_only(tmp_path: Path) -> None:
    csv_file = tmp_path / "empty.csv"
    result = run_cli(tmp_path, "export", str(csv_file))
    assert result.returncode == 0
    assert f"Exported 0 expense(s) to {csv_file}" in result.stdout

    with csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows == [["time", "amount", "category", "note"]]


def test_export_handles_legacy_records_without_time(tmp_path: Path) -> None:
    data_file = tmp_path / "expenses.json"
    data_file.write_text(
        json.dumps([{"amount": 10, "category": "misc", "note": "old"}]),
        encoding="utf-8",
    )
    csv_file = tmp_path / "legacy.csv"

    result = run_cli(tmp_path, "export", str(csv_file))
    assert result.returncode == 0

    with csv_file.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows == [["time", "amount", "category", "note"], ["", "10", "misc", "old"]]
