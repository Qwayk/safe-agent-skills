# Onboarding (non-technical)

This tool runs on your computer, and connects to a vendor API using an API key/token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview. When no saved snapshot is available for a supported write, the agent must say that clearly and ask for explicit no-snapshot approval before apply.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the required fields:
   - `ZENDESK_SUBDOMAIN` (or `ZENDESK_BASE_URL`)
   - `ZENDESK_EMAIL`
   - `ZENDESK_API_TOKEN`

## Step 2: Get your Zendesk API token (recommended auth)

This tool supports Zendesk API token auth (email + API token) using HTTP Basic auth.
You’ll create an API token in Zendesk Admin Center, then paste it into `.env`.

1) Identify your Zendesk subdomain:
   - If your Zendesk URL is `https://acme.zendesk.com`, your subdomain is `acme`.
2) Open Zendesk Admin Center, then go to:
   - **Apps and integrations** → **APIs** → **Zendesk API**
3) Enable **Token access** (if it’s not already enabled).
4) Click **Add API token**, then copy the token value.
5) Copy your Zendesk account email address (the email you log in with).
6) Fill in your `.env` (do not paste secrets into chat):

```bash
ZENDESK_SUBDOMAIN=acme
ZENDESK_EMAIL=you@company.com
ZENDESK_API_TOKEN=zd_api_token_here
```

Smoke test (offline by default; does not make a network call):

```bash
zendesk-api-tool --env-file .env --output json auth check
```

Optional live auth validation (safe read; makes one GET request):

```bash
zendesk-api-tool --env-file .env --output json --live auth check
```

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview and avoid live writes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Plan these metadata updates from a spreadsheet and show me the safe refusal if apply is attempted.”
- “Do a dry-run preview first. Do not apply live Zendesk writes.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
