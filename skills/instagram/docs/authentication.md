# Instagram Login Tool Authentication

This tool uses the official Instagram Login OAuth flow for Instagram professional accounts.

## Required app settings

Fill these values in `.env`:

- `INSTAGRAM_APP_ID`
- `INSTAGRAM_APP_SECRET`
- `INSTAGRAM_REDIRECT_URI`

You can also store a token in:

- `INSTAGRAM_ACCESS_TOKEN`, or
- `.state/token.json` written by the auth commands

## Scope names

Use only the scopes you need:

- `instagram_business_basic`: basic account reads and account lookup
- `instagram_business_content_publish`: create containers and publish media
- `instagram_business_manage_comments`: read, reply, hide, or delete comments
- `instagram_business_manage_messages`: send messages and private replies

Meta's insights docs also reference insights permissions. The current official docs mention `instagram_business_manage_insights` and `instagram_manage_insights` on the insights pages. If you plan to use the `insights` commands, check the latest official insights docs listed in `docs/references.md` before final app-review setup.

## Normal auth flow

1. Build a consent URL:

```bash
instagram-api-tool auth login-url --scope instagram_business_basic,instagram_business_manage_comments
```

2. Open that URL in a browser and sign in with the Instagram professional account.

3. Copy the `code` value from the redirect URL.

4. Token storage:

Auth write helpers create plans. When the tool cannot save useful old token state, apply requires explicit no-snapshot approval before token exchange or local token writes. To run reads today, you can also add a valid `INSTAGRAM_ACCESS_TOKEN` to `.env` yourself and keep it private.

5. Check token status without printing the token:

```bash
instagram-api-tool auth token status
```

6. Run the read-only smoke check:

```bash
instagram-api-tool auth check
```

## Refreshing a long-lived token

The refresh helper creates a plan first. When no useful old token state can be saved, apply requires explicit no-snapshot approval before the refresh request or local token write.

## Local token storage

Successful auth write helpers write token payloads to `.state/token.json` next to your `--env-file`. When no useful old token state can be saved, apply requires explicit no-snapshot approval before that file is written.

Rules:

- never commit `.state/`
- never paste token JSON into chat
- never put real secrets in docs or examples
