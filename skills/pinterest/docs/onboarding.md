# Connect your Pinterest account

Use this page when you want the shortest safe setup path for Pinterest work.

This skill runs on your machine and uses Pinterest credentials you store locally. You do not need to write code, but you do need the right Pinterest token and scopes for the work you want.

Keep this one rule in mind first: your `.env` file contains secrets. Keep it private and never paste it into chat.

## What you need

- A Pinterest access token for the fastest first test, or the app ID, app secret, and refresh token for longer-lived access.
- The Pinterest scopes needed for inventory, analytics, ads, or catalogs.
- An ad account ID if you want ads or catalogs work.
- A business ID if you want Business Access inventory.

## Step 1) Choose the auth path

You have two normal options:

1. a short-lived access token for the fastest first check
2. refresh-token auth for ongoing use

The full step-by-step lives in [Authentication details](authentication.md).

## Step 2) Fill the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Fill the values from [Configuration](configuration.md).
3. If you only want a fast first read test, start with the access token path.
4. If you want a longer-lived setup, fill the app and refresh-token values too.

## Step 3) Run the first safe checks

These are the best first commands:

```bash
pinterest-api-tool --output json --version
pinterest-api-tool --output json auth check
pinterest-api-tool --output json boards list --limit 1
```

If those commands work, the setup is good enough to start inventory snapshots or analytics checks.

For most people, the best next step is one board read and one audit snapshot before anything more advanced.

## What to ask your agent next

- "Confirm the Pinterest skill is connected, then export an audit snapshot of my boards and pins."
- "If analytics fails, rerun the snapshot without analytics and explain which permission is missing."
- "Preview a pin-link cleanup plan for these pins before any change goes live."

## If something fails

The most common causes are:

- an expired access token
- missing scopes
- missing ad-account or business access for the endpoints you want

Use [Troubleshooting](troubleshooting.md) if the auth check or first board read fails.
