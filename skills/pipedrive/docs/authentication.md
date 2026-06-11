# Authentication

This tool uses Pipedrive API token auth only.

## What you set

- `PIPEDRIVE_API_TOKEN`

The token goes in your local `.env` file.

## Safe check

Run:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
```

The command makes one safe read call to `/api/v1/users/me` and returns JSON.

The tool never prints token values.
