# Onboarding (non-technical)

This tool runs on your computer, and connects to the YouTube Data API v3 using an API key and/or OAuth token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview. For write attempts, the current tool requires explicit no-snapshot approval before changing YouTube when no saved snapshot is available.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Set at least one auth option:
   - API key (limited, mostly read-only): `YOUTUBE_API_KEY=...`
   - OAuth client secrets path (needed to plan OAuth login): `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json`

Notes:
- Do not commit `.env`.
- OAuth tokens are stored under `.state/token.json` (gitignored).

## Step 2: Get the API key/token (tool-specific)

You can use either an API key (limited, mostly read-only) or OAuth (recommended).

### Option A: OAuth (Desktop app) + blocked `auth login` plan

1) Open Google Cloud Console and select/create a project.
2) Enable the **YouTube Data API v3** for that project.
3) Go to **APIs & Services → Credentials** and create an **OAuth client ID**:
   - Application type: **Desktop app** (installed app)
4) Download the client secrets JSON file to your machine.
5) In your `.env`, set:

```bash
YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json
```

6) Run the login plan/refusal (console flow is the intended mode when token writing is later re-enabled):

```bash
youtube-api-tool auth login --console
```

7) Confirm no token was written by this blocked flow:

```bash
youtube-api-tool auth token status
youtube-api-tool auth check
```

### Option B (optional): API key (for some public reads)

1) In Google Cloud Console: **APIs & Services → Credentials**.
2) Create an **API key**.
3) In your `.env`, set:

```bash
YOUTUBE_API_KEY=YOUR_API_KEY
```

Note:
- OAuth is still required for many endpoints (including uploads).
- The tool never prints API keys or OAuth tokens to stdout/stderr/audit logs.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Preview these metadata updates from a spreadsheet and confirm the tool requires explicit no-snapshot approval before changing YouTube.”
- “Do a dry-run preview first. Only attempt after I approve, and confirm nothing changed.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Using an API key for an endpoint that requires OAuth
- Missing OAuth consent/scopes for the requested action

See: `docs/troubleshooting.md`.
