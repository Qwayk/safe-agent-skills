# Authentication

This tool supports two auth styles:

## 1) API key / token in `.env`

Optionally set `YOUTUBE_API_KEY` in `.env` (gitignored) for some public read-only endpoints.

## 2) OAuth (recommended)

OAuth is required for many endpoints (including uploads) and is recommended as your default.

### OAuth login (built-in)

1) Create/download OAuth client secrets JSON (Desktop app / installed app) from Google Cloud Console.
2) Point the tool at that file:
- `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json`
3) Generate the login plan/refusal (console mode is best for headless environments when this flow is later re-enabled):

```bash
youtube-api-tool auth login --console
```

Current safety status: `auth login` validates the client secrets file and scopes, then requires explicit no-snapshot approval before running the OAuth flow or writing `.state/token.json`. Existing token files can still be checked and redacted with the read-only token commands.

### Manual token import (advanced)

If you already have a token JSON file, this command now plans the storage action and requires explicit no-snapshot approval before writing local token state:

```bash
youtube-api-tool auth token set --file token.json
```

Check status (safe; never prints token values):

```bash
youtube-api-tool auth token status
```

Current safety status: `auth token set` does not write `.state/token.json` until local saved snapshot support is available.

Important:
- Never commit `.state/`
- Never print tokens in logs
