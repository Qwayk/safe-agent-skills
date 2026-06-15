# Configuration

Pipedrive configuration is the local setup an agent needs before it can review deals, people, organizations, activities, products, and pipeline data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Pipedrive values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy and fill.
- `.env`: local secrets file (not committed).
- Optional JSON config file passed via `--config` with non-secret defaults:
  - `base_url`
  - `api_domain`
  - `timeout_s`

## Environment variables

- `PIPEDRIVE_API_TOKEN` (required): token from Pipedrive.
- `PIPEDRIVE_API_DOMAIN` (optional): company domain or slug.
- `PIPEDRIVE_BASE_URL` (optional): full URL like `https://your-company.pipedrive.com`.
- `PIPEDRIVE_TIMEOUT_S` (optional, default `30`).

You only need one of `PIPEDRIVE_API_DOMAIN` or `PIPEDRIVE_BASE_URL`.
If the domain has no dot, the tool turns it into `https://<slug>.pipedrive.com`.
The token stays env-only and is not accepted from `--config`.

## OS override

OS variables override `.env` values when both are present.

## Config precedence

- `--config` provides fallback defaults for `base_url`, `api_domain`, and `timeout_s`.
- `.env` and OS env values override `--config`.
- `--timeout-s` CLI flag overrides both.
