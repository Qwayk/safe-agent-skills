# Onboarding (non-technical)

This tool runs on **your computer** and connects to Meta’s Graph/Marketing API using an access token you store **locally**.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.
- This tool is **read-only** (GET-only). It will not create/update/pause ads.

## Step 1: Create the local `.env` file

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill in `META_ADS_ACCESS_TOKEN`.
4) (Recommended) Fill in `META_ADS_AD_ACCOUNT_ID` (numeric id or `act_<id>`).

If you want the tool to guide you:

```bash
meta-ads-api-tool onboarding
```

## Step 2: Get a Meta access token (safe guidance)

Meta supports multiple token flows (short-lived user token, long-lived token, system user token).
This tool is compatible with any token that can make Graph API GET requests to the endpoints you use.

Minimum permissions/scopes (typical):
- `ads_read` (for most Marketing API reads and insights)

How to get a token (high level):
1) Use Meta for Developers to create/select an app.
2) Use a Meta-provided token tool (such as Graph API Explorer or Business Manager system user token generation) to generate an access token with `ads_read`.
3) Paste the token into `.env` as `META_ADS_ACCESS_TOKEN=...`.

Notes:
- Tokens can expire. If `auth check` starts failing later, regenerate a token and replace it in `.env`.
- Never paste the token into chat.

## Step 3: Find your Ad Account ID

You can usually find the numeric Ad Account ID in one of these places:
- Ads Manager UI: “Ad account settings” / account overview
- The Ads Manager URL often includes an `act=` parameter containing the numeric id

Paste into `.env` as either:
- `META_ADS_AD_ACCOUNT_ID=1234567890` (numeric), or
- `META_ADS_AD_ACCOUNT_ID=act_1234567890`

The tool normalizes numeric ids to `act_<id>` automatically.

## Step 4: Smoke test

Run:

```bash
meta-ads-api-tool --output json auth check
```

If you did not set `META_ADS_AD_ACCOUNT_ID`, you can also do:

```bash
meta-ads-api-tool --output json ad-accounts list --fields id,name
```

## What to ask your AI agent (examples)

- “List my ad accounts and show id + name.”
- “For ad account act_123…, list campaigns with id, name, status.”
- “Pull campaign insights for January 2026: impressions, clicks, spend.”

If the request is a write/mutation (pause ads, set budget), the agent should refuse and explain this tool is read-only.
