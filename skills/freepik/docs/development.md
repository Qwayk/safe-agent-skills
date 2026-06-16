# Development

This page is for maintainers changing the Freepik CLI. If you only want to use Freepik with an agent, start with the README, quickstart, or use cases.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Tests

```bash
python3 -m unittest -q
```

## Lint + types

```bash
ruff check src tests
mypy src tests
```

Before changing download behavior, also review the safety model so preview, approval, and saved-file handling stay clear.
