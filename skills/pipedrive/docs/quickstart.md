# Quickstart

This is a technical reference with commands.
If you are not technical, use `docs/use_cases.md` and `docs/onboarding.md` first.

1) Install dependencies.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Create `.env`.

```bash
cp .env.example .env
```

3) Start setup and check credentials.

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli onboarding
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
```

4) Run a read command.

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env --output json users get-current
```
