# Development

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

