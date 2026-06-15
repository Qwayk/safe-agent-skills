# Configuration

HubSpot configuration is the local setup an agent needs before it can review CRM records, contacts, companies, deals, tickets, and pipeline data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which HubSpot values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`).
- `.state/token.json`: optional OAuth token storage (gitignored).

`.state/token.json` is stored next to your `--env-file`.

## Environment variables

- `HUBSPOT_ACCESS_TOKEN` (primary auth token)
- `HUBSPOT_API_TOKEN` (optional compatibility fallback)
- `HUBSPOT_API_BASE_URL` (optional; default is `https://api.hubapi.com`)
- `HUBSPOT_TIMEOUT_S` (optional; default is `30`)

Command-line flags can override `.env`:
- `--env-file` for a custom file
- `--timeout-s` for timeout in seconds
