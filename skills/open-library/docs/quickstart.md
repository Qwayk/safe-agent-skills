# Quickstart

This is a technical reference with commands.
If you want the non-technical path first, start with `docs/use_cases.md` and `docs/onboarding.md`.

This tool is read-only and needs no auth key.
You can run it right away.

1) Install tool in this folder

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

2) Copy example config

```bash
cp .env.example .env
```

3) Optional: set your user-agent identity in `.env`

```bash
OPEN_LIBRARY_USER_AGENT_APP=qwayk-open-library-safe-agent-cli
OPEN_LIBRARY_CONTACT=you@example.com
```

4) Run a read-only command

```bash
qwayk-open-library-safe-agent-cli --output json search books --q "harry potter" --limit 3
```

Version command (no `.env` needed):

```bash
qwayk-open-library-safe-agent-cli --output json --version
```

If you prefer a separate config file for these values:

```bash
qwayk-open-library-safe-agent-cli --config local-open-library.json --output json search books --q "poetry"
```
