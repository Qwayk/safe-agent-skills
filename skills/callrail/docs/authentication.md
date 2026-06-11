# Authentication

This tool uses API-key auth only.

## 1) API key in `.env`

Put your CallRail API token in `.env` as `CALLRAIL_API_TOKEN`.
`auth check` is the built-in smoke test. It calls `GET /v3/a.json` with that token.

`auth check` uses these headers:
- `Authorization: Token token=<CALLRAIL_API_TOKEN>`
- `Request-From: <CALLRAIL_REQUEST_FROM>` (optional)

Optional environment variables:
- `CALLRAIL_API_BASE_URL` (required; `.env.example` already sets the official `https://api.callrail.com`)
- `CALLRAIL_DEFAULT_ACCOUNT_ID` (optional default for `--account-id`)
- `CALLRAIL_TIMEOUT_S` (timeout seconds)
- `CALLRAIL_REQUEST_FROM` (optional partner header)

The command:

```bash
qwayk-callrail-safe-agent-cli auth check
```

## 2) Write access and read-only keys

All write commands support plan/apply mode.
If your token is read-only, call will succeed for read routes and fail for writes with permission errors.

This tool does not ship any alternate auth mode or token-storage subcommands.

Important:
- Never commit your `.env`
- Never print token values in logs or paste output
