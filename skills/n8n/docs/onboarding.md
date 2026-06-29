# Connect n8n

Set up the n8n connection locally, then run one safe read before asking for any live change.

## Step 1: Create the local env file

In `api-tools/qwayk-n8n-safe-agent-cli/`:

```bash
cp .env.example .env
```

Open `.env` and fill:

```bash
N8N_BASE_URL=https://your-instance.app.n8n.cloud/api/v1
N8N_API_KEY=your_n8n_api_key
N8N_TIMEOUT_S=30
```

Keep `.env` private. Do not paste the API key into chat.

## Step 2: Create or choose an API key

Use n8n's API key settings for your instance. If your n8n plan supports scoped API keys, choose the narrowest key that can do the job.

For review-only work, prefer read scopes such as workflow, execution, project, tag, variable, or credential list/read scopes. For live changes, add only the specific create, update, delete, transfer, pull, stop, retry, package, or user scopes needed for that task.

## Step 3: Check the connection

```bash
PYTHONPATH=src python3 -m n8n_safe_agent_cli --env-file .env auth check
```

The check performs a read-only request to `/workflows?limit=1`. It confirms the base URL and API key work without changing n8n.

## Good first asks

- "Check the n8n connection and list what can be reviewed safely."
- "Show me the workflow and execution read commands, then stop."
- "Find recent failed executions and explain what to inspect next."
- "Prepare a plan to update this workflow, but do not apply it."

## If setup fails

- Confirm `N8N_BASE_URL` ends with `/api/v1`.
- Confirm the key belongs to the same n8n instance.
- Confirm the key has enough scope for the requested family.
- For n8n Cloud, make sure your plan allows public API access.
