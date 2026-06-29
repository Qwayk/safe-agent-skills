# Authentication

Make API calls use a token in the `Authorization` header.

Put the token in `.env` as `MAKE_API_TOKEN`. Never commit `.env` or paste the token into chat.

```bash
MAKE_BASE_URL=https://eu1.make.com
MAKE_API_TOKEN=<your_make_api_token>
```

The CLI sends the token as:

```text
Authorization: Token <value>
```

## Check access

Run:

```bash
make-com-safe --output json auth check
```

This checks `/users/me` when a token is present. It should return either a live status or a clear error without printing the token.

## OAuth token storage

Make also documents OAuth 2.0. The current helper stores token JSON safely for future OAuth-oriented workflows, but normal Make API use should start with `MAKE_API_TOKEN`.

1. Get a token JSON file from your approved OAuth flow.
2. Store it in the tool:

```bash
make-com-safe auth token set --file token.json
```

3. Check status. This should never print token values:

```bash
make-com-safe auth token status
```

Tokens are stored under `.state/token.json` next to your `--env-file`.

## Safety reminders

- Never commit `.state/`.
- Never print tokens in logs.
- Never paste keys, tokens, or OAuth files into chat.
