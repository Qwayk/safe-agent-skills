# Onboarding

This tool is read-only and does not need authentication for the normal public-page flow.

You do not need to be technical.
The shortest path is to give your agent the public status page URL and ask for the job you want done.

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
