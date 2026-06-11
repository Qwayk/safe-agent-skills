# Onboarding (non-technical)

This tool runs on your computer and connects to your Dynadot account using an API key that you keep locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will show a preview first, explain any approval it needs, and then give you a receipt or a clear blocker.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Get your Dynadot API key

In Dynadot:

1. Sign in to your account.
2. Open **Tools -> API**.
3. Create or reveal your API key.
4. If you have a stable IP, add an IP whitelist too.
5. Copy the key and keep it ready for your local `.env` file.

## Step 2) Fill the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill these fields:
   - `DYNADOT_API_KEY` with your real Dynadot API key
   - `DYNADOT_API_BASE_URL` and keep the default unless Dynadot tells you otherwise
   - `DYNADOT_TIMEOUT_S` only if you need a different timeout

## Step 3) Know the extra values some jobs need

- Domain pushes use a **Push Username**. Ask the receiver for that exact Dynadot push username first.
- Guided transfer runs between two Dynadot accounts need two local env files:
  - sender account as `--env-file`
  - receiver account as `--receiver-env-file`
- Transfer auth codes are sensitive. Save them to a local file instead of pasting them into chat.

## Step 4) What to ask your AI agent

These are plain-English requests. The safest path is always: read first, preview next, apply only after review.

- "Check the Dynadot tool is connected and show me my active domains."
- "Flag anything expiring soon and tell me what needs attention first."
- "Preview a push of these domains to another Dynadot account, but do not apply anything yet."
- "Show me a name server diff for these domains before any bulk change."
- "Plan the transfer run and explain whether this job needs no-snapshot approval before it can go live."

## If something fails

Common causes:
- missing or wrong values in `.env`
- API key restrictions or IP whitelist mismatch
- wrong receiver push username
- sender and receiver env files mixed up during a transfer workflow

See [Troubleshooting](troubleshooting.md) for symptoms and fixes.
