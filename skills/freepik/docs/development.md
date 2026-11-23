# Develop the Freepik tool

Use Python 3.12 or newer from the folder with `pyproject.toml`.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python3 -m unittest -q
ruff check src tests
mypy src tests
```

## Where the code lives

In `src/freepik_api_tool/`, `cli.py` parses commands, `config.py` loads account settings, and `project_config.py` reads local output paths. `freepik_api.py` calls the provider through `http.py`. Commands live in `commands/`. `commands/download.py` handles the preview and download steps for both single and batch work. `inventory.py` owns the CSV and file hashes.

Before changing a download, read the [approval rules](safety_model.md) and [inventory columns](inventory_schema.md). Check the JSON output, the saved preview and what happens to the files and CSV if one step fails. Test with simulated API replies first.
