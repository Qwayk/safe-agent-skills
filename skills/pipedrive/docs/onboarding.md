# Connect your Pipedrive account

Pipedrive needs a local API token before an agent can inspect deals, people, organizations, pipelines, and activities.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start by checking the current user or one pipeline before building a sales report.

## Step 1: Create the local `.env` file

Run onboarding once:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli onboarding
```

Then open `.env` and fill one of these connection paths:

```dotenv
PIPEDRIVE_API_DOMAIN=your-company
PIPEDRIVE_BASE_URL=https://your-company.pipedrive.com
PIPEDRIVE_API_TOKEN=
```

Use `PIPEDRIVE_API_DOMAIN` for the normal company slug. Use `PIPEDRIVE_BASE_URL` only when you need to provide the full URL.

## Step 2: Check the token

Run:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
```

Then run a small read:

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env --output json users get-current
```

If that works, the agent can safely inspect deals, leads, activities, people, and organizations.

## What to ask your AI agent

- Connect this Pipedrive read-only tool and check the token.
- Show me my current user profile from Pipedrive.
- List recent deals, leads, or activities for review.
- Search people or organizations by name.
