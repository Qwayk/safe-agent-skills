# Connect your Bluesky account

Bluesky needs your handle and an app password stored locally before an agent can check profiles, posts, sessions, or account data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a profile or session check before asking for any post or account action.

## What you need

- Your Bluesky handle or DID
- A Bluesky app password
- Optional custom service URLs only if you are working against non-default Bluesky services

## Step 1. Fill the local `.env` file

1. Copy `.env.example` to `.env`.
2. Fill:
   - `BLUESKY_IDENTIFIER`
   - `BLUESKY_APP_PASSWORD`
3. Leave the optional service URL overrides alone unless you already know you need them.

## Step 2. Log in once

```bash
bluesky-safe-cli --output json auth login
```

## Step 3. Run the first safe checks

```bash
bluesky-safe-cli --output json auth check
bluesky-safe-cli --output json api app-bsky-actor-get-profile --query-json '{"actor":"your-handle.bsky.social"}'
bluesky-safe-cli --output json --live api app-bsky-actor-get-profile --query-json '{"actor":"your-handle.bsky.social"}'
```

The second command is the preview. The third command is the first real live read.

## What to ask your agent next

- "Check the Bluesky skill is connected and show my profile safely."
- "List the operations for the area I need before we pick one."
- "Preview the exact write plan first and do not apply anything yet."

## If something fails

The most common causes are:

- the handle or DID is wrong
- the app password is missing or invalid
- the service URL overrides do not match the account you are using
- the account does not have permission for the endpoint you chose

Use [Troubleshooting](troubleshooting.md) if auth or the first live read fails.
