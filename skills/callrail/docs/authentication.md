# Authentication

CallRail authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because calls, forms, companies, trackers, messages, and account settings can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required CallRail environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

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
