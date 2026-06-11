# Configuration

This tool reads configuration from:
- a `.env` file specified by `--env-file` (default: `.env`)
- an optional JSON config file specified by `--config` (non-secret defaults)
- OS environment variables override values from the env file

CLI flags override everything:
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
