# Quickstart

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Configure

1. Copy `.env.example` to `.env`.
2. Set `SALESFORCE_INSTANCE_URL`.
3. Add a token in `.env` or store one with `auth token set`.

## Smoke checks

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --version
qwayk-salesforce-platform-safe-agent-cli --output json auth token status
qwayk-salesforce-platform-safe-agent-cli --output json auth check
```

## One read

```bash
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
```

## One write preview

```bash
qwayk-salesforce-platform-safe-agent-cli --output json composite execute --body-file composite.json
```

## One write apply refusal

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --apply --yes --plan-in plan.json composite execute --body-file composite.json
```

This apply request currently requires explicit no-snapshot approval before Salesforce HTTP when real before-state capture is not available for the write command.
