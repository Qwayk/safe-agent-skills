# Quickstart

Get one safe n8n result first: confirm the connection, then list the official workflow and execution commands your agent can use without changing anything.

## Install locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Add your n8n settings

```bash
cp .env.example .env
```

Fill `N8N_BASE_URL` and `N8N_API_KEY` in `.env`.

## First safe check

```bash
n8n-safe-agent-cli --env-file .env auth check
```

## List official operation commands

```bash
n8n-safe-agent-cli api list
```

## Read workflows

```bash
n8n-safe-agent-cli --env-file .env api workflow get-workflows --query limit=10
```

## Plan a workflow create without applying it

```bash
n8n-safe-agent-cli --env-file .env --plan-out plan.json api workflow create-workflow --body-file workflow.json
```

Review `plan.json`. A live apply is a separate step and must reuse the reviewed plan.
