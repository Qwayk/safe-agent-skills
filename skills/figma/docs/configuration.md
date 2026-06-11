# Configuration

The config is loaded from a `.env` file and optional OS environment variables.
OS environment variables always override `.env` values.

## Env file variables

- `FIGMA_BASE_URL` (default: `https://api.figma.com`)
- `FIGMA_AUTH_MODE` (`personal | oauth | plan`)
- `FIGMA_ACCESS_TOKEN` (PAT/plan token; optional for oauth mode)
- `FIGMA_TIMEOUT_S` (number; default `30`)

## OAuth token file behavior

When `FIGMA_AUTH_MODE=oauth`, the tool will:

1. Use `FIGMA_ACCESS_TOKEN` from env if it exists.
2. Otherwise read token JSON from `.state/token.json` next to `--env-file`.

The token file should look like:

```json
{ "access_token": "..." }
```

Only token metadata is shown by the tool, never raw token values.

## Config file locations

- `.env` (user-provided config)
- `.state/token.json` (optional OAuth token storage)

## Troubleshooting config

If commands fail to start:
- Check spelling of `FIGMA_AUTH_MODE` (must be one of `personal`, `oauth`, `plan`).
- Confirm token or `.state/token.json` is present for the selected mode.
- Confirm `FIGMA_TIMEOUT_S` is a positive number.
