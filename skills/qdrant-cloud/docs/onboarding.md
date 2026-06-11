# Connect your Qdrant Cloud account

Use this page when you want the shortest safe setup path for Qdrant Cloud work.

This skill runs on your machine and uses a Qdrant Cloud management API key that you store locally. You do not need to write code, but you do need the right key and the right account or cluster IDs for deeper jobs.

Keep this one rule in mind first: your `.env` file contains secrets. Keep it private and never paste it into chat.

## What you need

- A Qdrant Cloud management API key.
- The account ID for most real account, cluster, IAM, billing, or backup work.
- Cluster IDs, backup IDs, or other resource IDs when you move past the first inventory checks.

## Step 1) Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Add `QDRANT_CLOUD_API_KEY`.
3. If the key contains shell-special characters like `|`, wrap it in single quotes.
4. If your real env file lives elsewhere, plan to use `--env-file /full/path/to/.env`.

Example:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

## Step 2) Check optional settings only if you need them

Most people can leave the defaults alone.

Optional settings:

- `QDRANT_CLOUD_API_BASE_URL`
- `QDRANT_CLOUD_TIMEOUT_S`

You only need those if your environment requires a different base URL or timeout.

## Step 3) Run the first safe checks

These are the best first commands:

```bash
qdrant-cloud-api-tool --output json --version
qdrant-cloud-api-tool --output json auth check
qdrant-cloud-api-tool --output json --live auth check
qdrant-cloud-api-tool --output json --live account-v1 list-accounts
```

The offline `auth check` confirms config shape. The `--live` checks confirm that the key works against the real API.

## What to ask your agent next

- "Confirm the Qdrant Cloud skill is connected, then list my accounts and clusters."
- "Show me backups, backup schedules, and cluster recovery options for this account."
- "Preview this cluster or billing change and tell me what approval it needs before anything goes live."

## If something fails

The most common causes are:

- the key is missing or incorrect
- the wrong env file is being used
- the API key needs different account access
- `--live` was missing on a real API read

Use [Troubleshooting](troubleshooting.md) if the live auth check or account list fails.
