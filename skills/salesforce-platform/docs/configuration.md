# Configuration

This tool reads configuration from a local `.env` file. OS environment variables override the file values.

## Files

- `.env.example` -> copy to `.env`
- `.state/token.json` -> optional token storage written by `auth token set`
- `.state/runs/` -> local run history for write-capable commands

## Environment variables

- `SALESFORCE_INSTANCE_URL`
  - Example: `https://your-domain.my.salesforce.com`
- `SALESFORCE_API_VERSION`
  - Default: `67.0`
- `SALESFORCE_ACCESS_TOKEN`
  - Optional if you store the token with `auth token set`
- `SALESFORCE_TIMEOUT_S`
  - Default: `60`

## Notes

- `SALESFORCE_INSTANCE_URL` must start with `https://` or `http://`.
- `SALESFORCE_API_VERSION` should look like `67.0`. The tool adds the `v` prefix itself.
- Keep real tokens out of committed files and out of chat.
