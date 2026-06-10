# Onboarding

This tool needs a local `.env` file.

1) Run onboarding to create `.env` from `.env.example`:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli onboarding
```

2) Fill values:

- `PIPEDRIVE_API_DOMAIN=your-company`
- `PIPEDRIVE_API_TOKEN=YOUR_TOKEN`

Or use:

- `PIPEDRIVE_BASE_URL=https://your-company.pipedrive.com`

If your Pipedrive UI shows a full domain, use that in `PIPEDRIVE_API_DOMAIN`.

Required setup:
- `PIPEDRIVE_API_TOKEN`
- one of:
  - `PIPEDRIVE_API_DOMAIN`
  - `PIPEDRIVE_BASE_URL`

Optional:
- `PIPEDRIVE_TIMEOUT_S` (defaults to `30`)

3) Confirm setup:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
```

4) Keep `.env` private and never paste the token in chat.

## What to ask your AI agent

- Connect this Pipedrive read-only tool and check the token.
- Show me my current user profile from Pipedrive.
- List recent deals, leads, or activities for review.
- Search people or organizations by name.
