# Configuration

Statuspage configuration is the local setup an agent needs before it can review pages, components, incidents, subscribers, and status updates. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Statuspage values are required, which ones are optional, and confirm the setup without showing secrets."

## Where settings come from

Settings can come from:
- a `.env` file specified by `--env-file` (default: `.env`)
- an optional JSON config file specified by `--config` (non-secret defaults)
- OS environment variables override values from the env file

CLI flags override file and environment settings:
- `--base-url` overrides `STATUSPAGE_BASE_URL`
- `--timeout-s` overrides `STATUSPAGE_TIMEOUT_S`

## Required

- `STATUSPAGE_BASE_URL` (example: `https://status.atlassian.com`)

## Optional

- `STATUSPAGE_TIMEOUT_S` (seconds; default: `30`)

## JSON config file (optional)

Example `config.json`:

```json
{
  "base_url": "https://status.atlassian.com",
  "timeout_s": 30
}
```
