# Development

This page is for maintainers working on the Ghost CLI itself. If you only want an agent to use Ghost safely, start with `README.md`, `docs/quickstart.md`, or `docs/use_cases.md`.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Unit tests

```bash
python3 -m unittest -q
```

## Lint + types

```bash
ruff check src tests
mypy src tests
```

## CLI smoke checks (no credentials required)

```bash
ghost-api-tool --help
ghost-api-tool --version
```

Before opening a release change, run the tests and at least one no-credential CLI smoke check so simple packaging or command wiring problems are caught early.
