# Authentication

Bluesky authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because profile, post, graph, moderation, and session work can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Bluesky environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

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
