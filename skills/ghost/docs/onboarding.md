# Onboarding (non-technical)

This tool runs on your computer and connects to your Ghost Admin API using a **Custom Integration** key that you store locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Create a Ghost Custom Integration (recommended)

In Ghost Admin:

1) Go to **Settings → Integrations**.
2) Click **Add custom integration** (name it something like “API Tool”).
3) Copy the **Admin API Key** (it looks like `id:secret`). Make sure it’s the Admin key (not a Content key).
4) Copy the **Content API Key** (it’s a long string of characters; it’s read-only).
5) Copy the **API URL** shown in the same integration panel.

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `GHOST_ADMIN_API_URL` (paste the API URL from the integration, and ensure it ends with `/ghost/api/admin/`)
- `GHOST_ADMIN_API_KEY` (paste the Admin API Key)
- If you plan to run read-only Content API commands (`ghost-api-tool content ...`):
  - `GHOST_CONTENT_API_URL` (same domain, but ensure it ends with `/ghost/api/content/`)
  - `GHOST_CONTENT_API_KEY` (paste the Content API Key)
- `GHOST_ACCEPT_VERSION` (use the default unless your Ghost install requires a different value)

## Step 3) What to ask your AI agent (examples)

These are plain-English requests. The agent should start with read-only checks, then show a preview before applying changes.

- “Confirm the tool is connected, then audit my posts and summarize what looks risky or inconsistent.”
- “Export email delivery stats for my posts into a CSV.”
- “Audit internal links and produce a report (no changes).”
- “Preview deleting unused tags (zero posts). Apply only after I approve.”
- “Export member engagement, but keep emails redacted unless I explicitly approve otherwise.”

## If something fails

Common causes:
- Wrong API URL domain (Ghost(Pro) can have a different API domain than your public site domain)
- Wrong key type (Content key instead of Admin key, or vice versa)
- Wrong `Accept-Version`

See `docs/troubleshooting.md` for symptoms and fixes.
