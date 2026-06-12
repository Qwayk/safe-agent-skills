# Authentication

Use this page when you need to understand which YouTube credential to use and what the current OAuth helper can and cannot do.

This tool supports two auth styles.

## 1) API key / token in `.env`

Optionally set `YOUTUBE_API_KEY` in `.env` (gitignored) for some public read-only endpoints.

## 2) OAuth (recommended)

OAuth is required for many endpoints (including uploads) and is recommended as your default.

### Current OAuth limit

`youtube-api-tool auth login --console` can check the OAuth setup and show the planned token-write action, but this build does not write `.state/token.json`.

1. Create or download OAuth client secrets JSON from Google Cloud Console. Use **Desktop app**.
2. Point the tool at that file:
- `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json`
3. Inspect the login plan:

```bash
youtube-api-tool auth login --console
```

Existing token files can still be checked and redacted with the read-only token commands.

### Manual token import (advanced)

`youtube-api-tool auth token set --file token.json` also stops at the plan/refusal step today.

```bash
youtube-api-tool auth token set --file token.json
```

Check status (safe; never prints token values):

```bash
youtube-api-tool auth token status
```

If you already have a valid token JSON from another approved flow, place it at `.state/token.json`. The tool can then check token status and use it for supported OAuth reads or approved write planning.

Important:
- Never commit `.state/`
- Never print tokens in logs
