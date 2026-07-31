# Authentication

Authentication is handled by NameBright OAuth credentials in `.env`.

## Required settings

- `NAMEBRIGHT_CLIENT_ID`
- `NAMEBRIGHT_CLIENT_SECRET`

## Check auth before work

```bash
namebright-safe-cli --output json auth check
```

The command does not require API tokens or token file handoff. It uses OAuth client credentials to get a short-lived token.

To see token status fields (redacted), run:

```bash
namebright-safe-cli --output json auth token
```

## Safety reminders

- Never commit or print real credentials or token payloads.
- Never print verification codes or auth codes.
