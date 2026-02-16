# Expense Tracker CLI

Tiny Python CLI for tracking expenses in a local JSON file.

## Requirements

- Python 3.9+
- pytest (for running tests)

## Usage

Run commands as a module:

```bash
python -m expense_tracker --help
python -m expense_tracker add 12.50 food "Lunch with team"
python -m expense_tracker add 30 transport
python -m expense_tracker list
python -m expense_tracker total
python -m expense_tracker export expenses.csv
```

Data is stored in `expenses.json` at the repo root by default.

For testing or custom storage paths, set:

```bash
EXPENSE_TRACKER_FILE=/path/to/expenses.json python -m expense_tracker list
```

## Development

Run tests:

```bash
pytest -q
```
