# Connect your account

This skill runs on your computer and connects to Ghost with local API credentials that stay in your `.env` file.

You do not need to be technical. You can ask your agent to do the work for you, but the agent still needs the right Ghost API values on your machine first.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.
- The Ghost Admin API key is for management work and writes. The Content API key is optional and only used for public read-only content commands.

## Step 1) Create a Ghost Custom Integration

In Ghost Admin:

1. Go to **Settings → Integrations**.
2. Click **Add custom integration**.
3. Copy the **Admin API Key**. It looks like `id:secret`.
4. Copy the **API URL** shown in that integration panel.
5. If you also want public read-only Content API commands, copy the **Content API Key** from the same area.

## Step 2) Fill your local `.env` file

In the tool folder, copy `.env.example` to `.env` and fill:

- `GHOST_ADMIN_API_URL`
- `GHOST_ADMIN_API_KEY`
- `GHOST_ACCEPT_VERSION`

If you want Content API read-only commands too, also fill:

- `GHOST_CONTENT_API_URL`
- `GHOST_CONTENT_API_KEY`

Important URL shapes:

- Admin API URL should end with `/ghost/api/admin/`
- Content API URL should end with `/ghost/api/content/`

## Step 3) Ask for a safe auth check first

Before any real work, ask your agent to confirm the connection first.

Example:

- "Check that my Ghost skill is connected, then show me the latest posts and tags without changing anything."

## Step 4) Ask for the real job

These plain-English requests fit the normal safe workflow:

- "Audit my posts and summarize what looks risky or inconsistent."
- "Export email delivery stats for my posts into a CSV."
- "Audit internal links and produce a report with no changes."
- "Preview deleting unused tags with zero posts, but stop before apply."
- "Export member engagement, but keep emails redacted unless I explicitly approve otherwise."

## If something fails

Common causes:

- wrong API URL domain
- wrong key type
- wrong `Accept-Version`
- Content API values missing for `ghost-api-tool content ...` commands

See [Troubleshooting](troubleshooting.md) for common fixes.
