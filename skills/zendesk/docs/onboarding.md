# Connect your Zendesk account

Zendesk needs local subdomain and token settings before an agent can inspect tickets, users, organizations, views, and support queues.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a ticket count or small search before asking for support data changes.

## Step 1: Choose the auth mode you want

- **Zendesk email + API token** is the simplest setup and the recommended default.
- **OAuth bearer token** is also supported if your team already uses OAuth.

If you are unsure, start with the API token path.

## Step 2: Create the credentials in Zendesk

If you are using API token auth:

1. Identify your Zendesk subdomain.
   - If your Zendesk URL is `https://acme.zendesk.com`, the subdomain is `acme`.
2. Open Zendesk Admin Center.
3. Go to **Apps and integrations -> APIs -> Zendesk API**.
4. Enable **Token access** if it is not already enabled.
5. Click **Add API token** and copy the token value.
6. Keep your Zendesk login email ready too.

If your team uses OAuth instead, get the bearer token from your approved internal flow and keep it private for `.env`.

## Step 3: Fill the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill one of these setups:
   - API token setup:
     - `ZENDESK_SUBDOMAIN=acme` or `ZENDESK_BASE_URL=https://acme.zendesk.com`
     - `ZENDESK_EMAIL=you@company.com`
     - `ZENDESK_API_TOKEN=...`
   - OAuth setup:
     - `ZENDESK_SUBDOMAIN=acme` or `ZENDESK_BASE_URL=...`
     - `ZENDESK_OAUTH_ACCESS_TOKEN=...`

## Step 4: Ask for safe first checks

These are good first requests for your agent:

- “Confirm the Zendesk skill is connected and show the safest read options first.”
- “Validate the pinned Zendesk inventory and show me the main ticket read commands.”
- “Find the right tickets or users safely, but stop before any changes.”
- “Plan these Zendesk updates from a spreadsheet and show me the approval gate before live writes.”

## If something fails

The most common issues are:
- missing or wrong values in `.env`
- wrong key type or missing Zendesk permissions
- network or auth restrictions in your Zendesk account
- forgetting that even safe reads may return sensitive support data

See [Troubleshooting](troubleshooting.md) for the common error paths and fixes.
