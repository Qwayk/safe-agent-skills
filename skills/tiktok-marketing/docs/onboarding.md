# Connect your TikTok Marketing account

TikTok Marketing needs local app credentials and advertiser access before an agent can inspect accounts, campaigns, creatives, and credential health.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start by confirming advertiser access before asking for campaign or spend work.

## What you need

- `TIKTOK_MARKETING_APP_ID`
- `TIKTOK_MARKETING_APP_SECRET`
- `TIKTOK_MARKETING_ACCESS_TOKEN`, or a local `.state/token.json` token file
- The right advertiser permissions for the live operations you want to use

## Step 1. Create the local `.env` file

The easiest path is one of these:

1. run `tiktok-marketing-api-tool --output json onboarding`
2. or copy `.env.example` to `.env`

Then fill:

- `TIKTOK_MARKETING_API_BASE_URL=https://business-api.tiktok.com`
- `TIKTOK_MARKETING_APP_ID`
- `TIKTOK_MARKETING_APP_SECRET`
- `TIKTOK_MARKETING_ACCESS_TOKEN`

## Step 2. Use the token-file path only if you need it

If you want token-file auth instead of an env token:

```bash
tiktok-marketing-api-tool --output json auth token set --file token.json
tiktok-marketing-api-tool --output json auth token status
```

`auth check` uses `.state/token.json` only when `TIKTOK_MARKETING_ACCESS_TOKEN` is missing.

## Step 3. Run the first safe checks

These are the best first commands:

```bash
tiktok-marketing-api-tool --output json --version
tiktok-marketing-api-tool --output json auth check
tiktok-marketing-api-tool --output json api ops list
tiktok-marketing-api-tool --output json api ops show --op oauth2-advertiser-get
```

The important truth here is that `auth check` is already a live helper. It does not need `--live`. The broader `api` surface still uses `--live` for real provider reads.

## What to ask your agent next

- "Can you check if my TikTok Marketing access settings are valid before I run anything else?"
- "Can you draft one safe campaign or advertiser read for me to review first?"
- "Can you show me the exact pinned operation before we try a live TikTok read?"

## If something fails

The most common causes are:

- wrong or missing app credentials
- expired or missing token
- missing advertiser permissions
- missing required request JSON for the operation you picked

Use [Troubleshooting](troubleshooting.md) if the auth check or the first planned read fails.
