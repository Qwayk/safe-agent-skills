# Development

## Setup (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Unit tests

```bash
python3 -m unittest -q
```

Add new commands under `src/wordpress_api_tool/commands/` and keep the safety rules (dry-run + verify).

## Lint + types

```bash
ruff check src tests
mypy src tests
```

## Run without installing (optional)

```bash
PYTHONPATH=src python3 -m wordpress_api_tool --version
```
