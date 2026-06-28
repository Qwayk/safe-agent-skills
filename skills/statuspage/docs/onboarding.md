# Use Statuspage with no account

Statuspage can start from a public status page URL. You do not need an account or API key for normal incident and maintenance checks.

No secrets are needed for the first run. If the tool creates a local `.env` file, treat it as local setup only; it should not contain a private service token.

Start by giving the agent the exact public status page URL you want reviewed.

## Fastest first run

Give your agent a public Statuspage URL like:

- `https://status.atlassian.com`

Then ask for one of these:

- “Check this status page and tell me if anything is down.”
- “Show me open incidents on this status page.”
- “Tell me if there is planned maintenance.”
- “Summarize the current component status for this page.”

## Optional repeat setup for direct CLI use

If you want to run the CLI yourself more than once, you can keep the base URL in a local `.env` file:

1. Copy `.env.example` to `.env`.
2. Set `STATUSPAGE_BASE_URL=https://status.somevendor.com`.

Keep `.env` local on your machine.

## What to avoid

- Do not ask for private incident data from a public Statuspage URL. This tool reads what the page exposes publicly.
- Do not rely on a summary alone during an outage. Ask the agent to show the incident title, status, affected components, and latest update time.
