# Onboarding (non-technical)

This tool uses local `.env` settings and the official Threads OAuth + Graph APIs.

Keep these private:
- `.env`
- app secret
- access tokens

## Step 1: Create `.env`

Copy `.env.example` to `.env`, then fill:
- `THREADS_API_BASE_URL=https://graph.threads.net`
- `THREADS_API_VERSION=v1.0`
- `THREADS_APP_ID=<your app id>`
- `THREADS_APP_SECRET=<your app secret>`
- `THREADS_REDIRECT_URI=<your redirect uri>`
- `THREADS_DEFAULT_USER_ID=<optional default account id>`

## Step 2: Build the authorize URL

For a read-first setup:

```bash
threads-api-tool --output json auth authorize-url --scope threads_basic
```

For a broader setup that includes publishing:

```bash
threads-api-tool --output json auth authorize-url --scope threads_basic,threads_content_publish
```

Add extra Threads permissions only when you need them:
- `threads_profile_discovery`
- `threads_manage_mentions`
- `threads_manage_insights`
- `threads_read_replies`
- `threads_manage_replies`
- `threads_keyword_search`
- `threads_location_tagging`
- `threads_delete`

## Step 3: Exchange the code

```bash
threads-api-tool --output json --plan-out /tmp/threads-auth.plan.json auth code exchange --code <authorization_code>
```

If you want the tool to exchange and save the token for you, review the plan first. Token exchange and `.state/token.json` writes need explicit no-snapshot approval when no saved snapshot exists.

If you only want read access first, you can also place a valid `THREADS_API_TOKEN` in your local config and skip token-writing flows for now.

## Step 4: Confirm setup

```bash
threads-api-tool --output json auth check
threads-api-tool --output json auth token status
```

## Step 5: What to ask your AI agent first

- “Check the Threads skill is connected and show my profile.”
- “List my recent owned posts and tell me how much posting room is left.”
- “Look up this public Threads account and list recent posts.”
- “Prepare a post or reply action, but stop before any live write.”

## What this CLI does not do

- It does not expose Web Intents as CLI commands.
- It does not manage webhook dashboard setup or topic subscriptions for you.
