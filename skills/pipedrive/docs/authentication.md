# Authentication

Pipedrive authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because CRM deals, leads, activities, people, organizations, products, and pipelines can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Pipedrive environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

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
