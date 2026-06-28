# Development

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
