# Authentication

Mercury authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because business banking balances, accounts, transactions, cards, recipients, and local exports can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Mercury environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Configure `.env` (recommended)

Put your Mercury API token in `.env` (gitignored):

- `MERCURY_API_TOKEN=secret-token:...`

Choose an auth scheme (default: bearer):

- `MERCURY_AUTH_SCHEME=bearer` (sends `Authorization: Bearer <token>`)
- `MERCURY_AUTH_SCHEME=basic` (sends HTTP Basic with `username=<token>` and empty password)

Then run a read-only smoke check:

```bash
mercury-api-tool --output json auth check
```

Important:
- Never commit `.env` or any token files.
- Never paste tokens into chat.
