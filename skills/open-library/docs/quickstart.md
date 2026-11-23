# Run your first book search

Open a terminal in the skill folder that contains `pyproject.toml`. Use Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
qwayk-open-library-safe-agent-cli --output json search books --q "dune" --limit 3
```

The search uses Open Library's public catalog. It works without an account, API key or settings file. Look for `"ok": true` and titles under `data.docs`. An empty list means there were no matches on that page.

If a title looks right, use its `key` with `works get`. To check a particular edition, use its ISBN or edition ID. [See the commands and what to do if a read fails](command_reference.md).
