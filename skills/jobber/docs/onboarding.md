# Connect your Jobber account

Jobber needs local OAuth settings and token state before an agent can inspect account areas, clients, jobs, requests, invoices, or scheduling data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with an access check and a small read before asking for service-business changes.

## Step 1: Add local settings

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Keep any local secrets out of git and out of chat.
3. Keep `JOBBER_API_BASE_URL` as `https://api.getjobber.com` unless your setup needs another base URL.

## Step 2: Configure OAuth 2.0 credentials

Create a Jobber app in the Jobber Developer Center and add:

- Client ID
- Client Secret
- Redirect URI used by your app callback

Then add them to `.env`:

- `JOBBER_CLIENT_ID`
- `JOBBER_CLIENT_SECRET`
- `JOBBER_REDIRECT_URI`

When available, add your preferred API version:
- `JOBBER_GRAPHQL_VERSION` (defaults to `2025-04-16` if missing)

## Step 3: Connect a token

1. Ask your agent or run:
   - `qwayk-jobber-safe-agent-cli auth authorize-url`
2. Complete Jobber OAuth flow and collect the token JSON.
3. Save the token JSON with:
   - `qwayk-jobber-safe-agent-cli auth token set --file token.json`
4. Confirm with:
   - `qwayk-jobber-safe-agent-cli auth token status`

## Step 4: Verify

- Run `qwayk-jobber-safe-agent-cli auth check`.
- Fix any missing config before moving to commands.

## Step 3: What to ask your AI agent (examples)

- “Check that the skill is connected and tell me what it can safely review.”
- “Show me which accounts and areas are currently readable with this token.”
- “Prepare a safe plan for this change and stop before any writes.”
- “Give me the next best step after the first account check.”

## What success looks like

Setup is working when:
- `auth check` confirms token availability and account probe.
- The tool can list read families from schema helpers.
- No secret values are exposed in responses.

If you want the command version, continue with [Quickstart](quickstart.md).
