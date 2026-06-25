# Connect your Contentsquare account

Start the same way you would start a careful Contentsquare review: connect the local OAuth credentials, confirm the token endpoint, run one small read, then stop before any change.

You do not need to learn every command first. Contentsquare setup has two parts: local server-to-server OAuth credentials, and enough Contentsquare entitlement for the API family you want the agent to inspect.

Keep the setup files private. Do not paste `.env`, client secrets, OAuth responses, access tokens, or exported data into chat.

## Step 1: Create the local settings file

From the tool folder:

```bash
cp .env.example .env
```

Keep `.env` private and local.

## Step 2: Get OAuth credentials

In the Contentsquare console, create server-to-server OAuth credentials for the API areas you plan to use.

Fill these local values:

```bash
CONTENTSQUARE_CLIENT_ID=...
CONTENTSQUARE_CLIENT_SECRET=...
CONTENTSQUARE_PROJECT_ID=
CONTENTSQUARE_AUTH_BASE_URL=https://api.contentsquare.com
CONTENTSQUARE_API_BASE_URL=
CONTENTSQUARE_TIMEOUT_S=30
```

Leave `CONTENTSQUARE_API_BASE_URL` empty unless Contentsquare gives you a fixed API endpoint. The OAuth response can return the right API endpoint for your cloud.

If your OAuth credentials were created at the account level, fill `CONTENTSQUARE_PROJECT_ID` with the project you want the token to target. You can also pass `--oauth-project-id` for one command.

## Step 3: Confirm the connection

```bash
contentsquare-safe-cli auth check
```

A good result returns `ok: true`, confirms a token was obtained for the default `data-export` scope, and shows the API endpoint without printing the token or secret. This is still only a setup check. The first live Contentsquare proof is one safe read against a project or object list you recognize.

## Step 4: What to ask your AI agent

- “Run the Contentsquare onboarding command and tell me what is missing.”
- “Check Contentsquare auth and confirm no secrets are printed.”
- “List export jobs for project 123.”
- “Show site visits for project 123 last week.”
- “Tell me which Contentsquare API family is safe to read first before preparing any change.”

## What success looks like

Setup is working when the agent can:

- confirm OAuth credentials are present without printing secrets
- name the API endpoint returned by Contentsquare or configured locally
- explain whether a project id is needed for account-level credentials
- run one read-only request that your Contentsquare permissions allow
- stop before any live change

If auth works but a real API read fails, setup is only partly working. The usual missing piece is the project id, API family entitlement, date range, integration id, or Contentsquare permission.
