from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from .storage import StorageError, default_data_file, load_expenses, save_expenses


def positive_amount(value: str) -> float:
    try:
        amount = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("amount must be a number") from exc
    if amount <= 0:
        raise argparse.ArgumentTypeError("amount must be greater than 0")
    return amount


def data_file_from_env() -> Path:
    override = os.environ.get("EXPENSE_TRACKER_FILE")
    return Path(override) if override else default_data_file()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m expense_tracker",
        description="Track expenses in a local JSON file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add an expense entry.")
    add_parser.add_argument("amount", type=positive_amount, help="Expense amount (must be > 0).")
    add_parser.add_argument("category", help="Expense category, e.g. food, rent, travel.")
    add_parser.add_argument("note", nargs="?", default="", help="Optional note.")
    add_parser.set_defaults(func=handle_add)

    list_parser = subparsers.add_parser("list", help="List all saved expenses.")
    list_parser.set_defaults(func=handle_list)

    total_parser = subparsers.add_parser("total", help="Show the total amount spent.")
    total_parser.set_defaults(func=handle_total)

    export_parser = subparsers.add_parser("export", help="Export all expenses to a CSV file.")
    export_parser.add_argument("csv_filename", help="Output CSV filename/path.")
    export_parser.set_defaults(func=handle_export)

    return parser


def handle_add(args: argparse.Namespace) -> int:
    data_file = data_file_from_env()
    expenses = load_expenses(data_file)
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "amount": args.amount,
        "category": args.category,
        "note": args.note,
    }
    expenses.append(entry)
    save_expenses(data_file, expenses)
    note = f" | {args.note}" if args.note else ""
    print(f"Added: ${args.amount:.2f} | {args.category}{note}")
    return 0


def handle_list(args: argparse.Namespace) -> int:
    del args
    data_file = data_file_from_env()
    expenses = load_expenses(data_file)
    if not expenses:
        print("No expenses recorded.")
        return 0
    for idx, item in enumerate(expenses, start=1):
        note = item.get("note", "") or "-"
        print(f"{idx}. ${float(item['amount']):.2f} | {item['category']} | {note}")
    return 0


def handle_total(args: argparse.Namespace) -> int:
    del args
    data_file = data_file_from_env()
    expenses = load_expenses(data_file)
    total = sum(float(item["amount"]) for item in expenses)
    print(f"Total: ${total:.2f}")
    return 0


def handle_export(args: argparse.Namespace) -> int:
    data_file = data_file_from_env()
    expenses = load_expenses(data_file)
    output = Path(args.csv_filename)
    try:
        with output.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["time", "amount", "category", "note"])
            for item in expenses:
                writer.writerow(
                    [
                        item.get("time", ""),
                        item.get("amount", ""),
                        item.get("category", ""),
                        item.get("note", ""),
                    ]
                )
    except OSError as exc:
        raise StorageError(f"Could not write {output}") from exc
    print(f"Exported {len(expenses)} expense(s) to {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except StorageError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")
