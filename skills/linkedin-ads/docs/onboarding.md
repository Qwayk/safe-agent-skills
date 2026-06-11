# Onboarding

This page helps you run the CLI safely from your local machine.

`linkedin-ads-api-tool` uses a local `.env` file plus a local token file.

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

Keep `.env` private.

## Step 2: add a token

If you want to set token in another key, use one of these:

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

## Step 4: first safe commands

Start with read commands.

```bash
linkedin-ads-api-tool ad-account-users list-authenticated-user
linkedin-ads-api-tool ad-campaigns search --ad-account-id 123456
```

Both commands run live and do not need `--apply`.
