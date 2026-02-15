# AGENTS.md (Codex demo)

## Working rules
- Do not ask me questions unless you are blocked; make reasonable assumptions and proceed.
- Always add or update automated tests for any behavior you add.
- Always run tests locally before finishing and report the results.
- Keep changes small and easy to review.

## Definition of done
- All tests pass.
- Clear CLI help text.
- Edge cases covered by tests.

## Project
Build a tiny CLI expense tracker in Python.

Commands:
- add <amount> <category> [note]
- list
- total

Data must persist in a local JSON file inside the repo.
