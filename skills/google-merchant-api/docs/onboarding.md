# Onboarding (non-technical)

Use this flow first to start using the tool safely.

## Step 1: Copy the local config file

1. In this folder, run:
   - `cp .env.example .env`
2. Open `.env` and set one auth mode:
   - `GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json` for service-account access (simplest own-account path)
   - `GOOGLE_MERCHANT_API_AUTH_MODE=oauth_refresh_token` for client-account access
   - `GOOGLE_MERCHANT_API_AUTH_MODE=adc` if running on Google-hosted systems only (optional helper)
3. Set `GOOGLE_MERCHANT_API_BASE_URL`.
4. Keep `.env` private and never paste it in chat.

## Step 2: First safe auth check

Use this first before API calls:

- `google-merchant-api-tool --output json auth check`

This command only validates credentials and prints a redacted status.

## Step 3: Start with reads and write previews

The tool starts in dry-run mode for writes. Current `--apply` write attempts require explicit no-snapshot approval when no useful before-state can be captured; approved supported writes can proceed and produce receipts with recovery limits.

Examples:
- `google-merchant-api-tool accounts list`
- `google-merchant-api-tool accounts products list --parent accounts/123456`
- `google-merchant-api-tool accounts product-inputs insert --parent accounts/123456 --body-file product.json` (preview-first)

## What to ask your AI agent (examples)

- Ask for a safe first check and a short action plan:
  "Can you check if the tool is connected and then map my Merchant structure before I ask for changes?"
- Ask for a catalog discovery summary:
  "Can you list the top 5 account-level checks I should run before editing products?"
- Ask for a low-risk improvement set:
  "Find policy or feed issues in my account and group them by fix type."
- Ask for a staging workflow:
  "Run a full dry-run for a title/price update and show me the plan, needed approval, and receipt path."

## Step 4: Auth field map

- `GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON` for service account mode
- `GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN` for OAuth refresh-token mode
- `GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID` and `GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET` for OAuth mode

## Common setup errors

- Missing `.env` values (for example `GOOGLE_MERCHANT_API_BASE_URL` or auth fields).
- Wrong auth mode for the account setup.
- OAuth token file has placeholder values.
- Token mode missing client credentials.
