# Authentication

## Primary auth path

Use handle or DID + app password via `com.atproto.server.createSession`.

1) Add values to `.env`:
- `BLUESKY_IDENTIFIER` (handle or DID)
- `BLUESKY_APP_PASSWORD` (app password)

2) Run:

```bash
bluesky-safe-cli auth login
```

`auth login` creates a Bluesky session and saves it locally.

## Extra auth helpers

- `bluesky-safe-cli auth check`  
  Checks current auth state and session status.
- `bluesky-safe-cli auth refresh`  
  Refreshes the local session.
- `bluesky-safe-cli auth logout`  
  Clears local session files.
- `bluesky-safe-cli auth token set --file token.json`  
  Copies a token JSON into `.state/token.json`.
- `bluesky-safe-cli auth token status`  
  Shows where a token file exists and available fields.

## Where values are stored

The local auth/session file is `.state/token.json` under your `--env-file` folder.

Important:
- Do not print token values.
- Do not commit `.state/token.json`.
