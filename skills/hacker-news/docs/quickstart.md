# Fetch your first Hacker News story

Open a terminal in the skill folder where `pyproject.toml` lives. Use Python 3.12 or newer to install the CLI in its own environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
hacker-news-api-tool --output json items get --id 8863
```

The command uses the public Hacker News API. It works without an account or a settings file. Look for `"ok": true` and `"id": 8863` in the result.

To see what is on the top list now, run:

```bash
hacker-news-api-tool --output json stories top
```

Open the IDs you want to read with `items get --id` before you summarize the stories. [See all the commands and what to do if a read fails](command_reference.md).
