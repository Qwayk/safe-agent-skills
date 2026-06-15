# Authentication

Microsoft Ads authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For accounts, campaigns, budgets, ads, keywords, audiences, and reports, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Microsoft Ads credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Authentication notes

Microsoft Ads uses OAuth for user authentication/authorization, plus a separate `DeveloperToken`.

## OAuth token storage (manual copy/paste)

1) Obtain an OAuth token JSON file from your OAuth process (auth code + refresh token).
2) Store it locally in the tool:

```bash
msads-api-tool auth token set --file token.json
```

3) Check status (safe; never prints token values):

```bash
msads-api-tool auth token status
```

Tokens are stored under `.state/token.json` next to your `--env-file`.

Where the OAuth token comes from:
- Microsoft Ads OAuth uses an authorization code flow and yields a refresh token.
- The official setup steps are linked in `docs/references.md` under “OAuth”.

## Developer token

Put your Microsoft Ads `DeveloperToken` in `.env`:
- `MSADS_DEVELOPER_TOKEN=...`

Where the DeveloperToken comes from:
- You request a DeveloperToken from Microsoft Advertising (see the official “Get started” and account/permissions docs linked in `docs/references.md`).
- Some accounts require approval before the token is usable for production access.

Important:
- Never commit `.state/`
- Never print tokens in logs
