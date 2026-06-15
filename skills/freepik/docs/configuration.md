# Configuration

Freepik configuration is the local setup an agent needs before it can search assets, review downloads, and work with licensed creative material. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Freepik values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

This page documents the supported env vars for `freepik-api-tool`.

Recommended workflow:
- keep secrets in a local `.env` file (gitignored),
- use CLI flags for one-off overrides,
- never store keys in tracked files.

## Required

- `FREEPIK_API_KEY`: Freepik API key.

## Optional (common)

- `FREEPIK_API_BASE_URL` (default: `https://api.freepik.com/v1`)
- `FREEPIK_BASE_URL` (alias for `FREEPIK_API_BASE_URL`)
- `FREEPIK_TIMEOUT_S` (default: `30`)
- `FREEPIK_ACCEPT_LANGUAGE` (default: empty)
- `FREEPIK_IMAGE_SIZE` (default: empty)

## Optional (advanced)

Auth header overrides:
- `FREEPIK_AUTH_HEADER` (default: `x-freepik-api-key`)
- `FREEPIK_AUTH_PREFIX` (default: empty)

Response parsing overrides (only if the API response shape changes):
- `FREEPIK_DOWNLOAD_URL_JSONPATH`
- `FREEPIK_LICENSE_URL_JSONPATH`

## Notes
- `FREEPIK_*_JSONPATH` uses a simple dot/bracket syntax and is only needed if auto-detection fails.
- If you set these, validate with a dry-run download plan and inspect the `no_snapshot_available` before-state output. Approved licensed download still needs explicit `--ack-no-snapshot` when no saved snapshot is available.
