# Authentication

LinkedIn Ads authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For ad accounts, campaigns, creatives, audiences, lead forms, and reports, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which LinkedIn Ads credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Supported token inputs

Use this key first:
- `LINKEDIN_ADS_TOKEN`

Other accepted keys:
- `LINKEDIN_ADS_ACCESS_TOKEN`
- `LINKEDIN_ADS_API_TOKEN`

If none are set, the tool also reads from `.state/token.json` (saved via `auth token set`).

## Command flow

1) Optional manual token save:

```bash
linkedin-ads-api-tool auth token set --file token.json
```

This writes the token JSON path from your `--env-file`, usually:

```bash
.state/token.json
```

2) Check token setup:

```bash
linkedin-ads-api-tool auth token status
```

This check only shows token-file presence and path.

3) Verify live auth:

```bash
linkedin-ads-api-tool auth check
```

This runs a safe live GET to:

`GET /adAccountUsers?q=authenticatedUser`

## Safe error behavior

Errors do not include raw token text.
If the token is bad or missing, output still stays machine-safe.
