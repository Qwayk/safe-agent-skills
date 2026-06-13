# Connect your Google Ads account

Google Ads needs local API credentials before an agent can check accounts, customer IDs, presets, or campaign data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start by confirming the accessible customer IDs before asking for campaign analysis or any change that can affect spend.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.

Or run:

- `google-ads-api-tool onboarding`

## Step 2: Get the required Google Ads API credentials

You need all of the following:

1. **Google Ads developer token**
   - Request a developer token in Google Ads (approval may take time).
   - Paste into `.env`:
     - `GOOGLE_ADS_DEVELOPER_TOKEN=YOUR_GOOGLE_ADS_DEVELOPER_TOKEN`

2. **OAuth2 client id + client secret**
   - Create an OAuth client in Google Cloud Console (see `docs/references.md`).
   - Paste into `.env`:
     - `GOOGLE_ADS_CLIENT_ID=YOUR_GOOGLE_ADS_CLIENT_ID`
     - `GOOGLE_ADS_CLIENT_SECRET=YOUR_GOOGLE_ADS_CLIENT_SECRET`

3. **OAuth2 refresh token (Google Ads API scope)**
   - Generate a refresh token for the Google Ads API scope (see `docs/references.md`).
   - Paste into `.env`:
     - `GOOGLE_ADS_REFRESH_TOKEN=YOUR_GOOGLE_ADS_REFRESH_TOKEN`

Optional:
- If you use a manager/MCC context, set:
  - `GOOGLE_ADS_LOGIN_CUSTOMER_ID=YOUR_MANAGER_CUSTOMER_ID` (digits only)

## Step 3: Smoke test

Run:

- `google-ads-api-tool --output json auth check`
- `google-ads-api-tool --output json customers list-accessible`

## Step 4: First GAQL query

Pick a customer id you can access and run a tiny query:

- `google-ads-api-tool --output json gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT customer.id FROM customer LIMIT 1" --limit 1`

## Step 5: Fast safe write paths

For common edits, use helpers:
- `google-ads-api-tool --output json helpers campaign set-budget --customer-id YOUR_CUSTOMER_ID --budget-id YOUR_BUDGET_ID --amount 70`

For whole campaign creation, use builders:
- `google-ads-api-tool --output json builders search-campaign from-spec --spec ./docs/examples/inputs/builder_search_campaign_spec.json`

## If something fails

Most common issues:
- Missing or incorrect values in `.env`
- Developer token not approved/allowed for your account type
- OAuth refresh token created for the wrong scope

See `docs/troubleshooting.md` and `docs/references.md`.
