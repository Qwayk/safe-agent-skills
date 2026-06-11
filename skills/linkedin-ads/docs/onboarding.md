# Onboarding (non-technical)

This tool runs on your computer and connects to LinkedIn Ads with a local token and local config.

You do not need to be technical. You can ask an AI agent to do the LinkedIn Ads work, and the agent should start with a safe access check before it plans anything risky.

Important:
- Keep your `.env` file and any token JSON private. Never paste them into chat.

## Step 1: create `.env` with safe defaults

Run:

```bash
linkedin-ads-api-tool onboarding
```

If no `.env` exists, this writes a new file with:

- `LINKEDIN_ADS_BASE_URL`
- `LINKEDIN_ADS_TOKEN` (main field written by onboarding)
- `LINKEDIN_ADS_LINKEDIN_VERSION`
- `LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION`
- `LINKEDIN_ADS_TIMEOUT_S`

This creates a local `.env` with placeholders only when one is missing.

## Step 2: add a token

If you already have a LinkedIn token from your approved app flow, you can store it in any of these keys:

- `LINKEDIN_ADS_ACCESS_TOKEN`
- `LINKEDIN_ADS_TOKEN`
- `LINKEDIN_ADS_API_TOKEN`

You can also store token JSON with:

```bash
linkedin-ads-api-tool auth token set --file token.json
```

The token file is saved at `.state/token.json` beside your `--env-file`.

## Step 3: check your approval and account access

Run:

```bash
linkedin-ads-api-tool --output json auth check
```

This reads `GET /adAccountUsers?q=authenticatedUser` to verify the token works.

If LinkedIn blocks you, it means your app may still be in approval or product-gate mode.
LinkedIn can reject all reads and writes until the app owner flow is approved.

## Step 4: what to ask your AI agent first

These are safe plain-English starting requests:

- “Check whether this LinkedIn Ads token works and list the ad accounts I can access.”
- “Show me one campaign search and one analytics pull for this ad account.”
- “Tell me which LinkedIn Ads product areas are still access-gated before we plan anything.”
- “Prepare a change plan for this campaign, but stop before any live apply.”

## Step 5: first safe commands

Start with read commands.

```bash
linkedin-ads-api-tool ad-account-users list-authenticated-user
linkedin-ads-api-tool ad-campaigns search --ad-account-id 123456
```

Both commands run live and do not need `--apply`.
