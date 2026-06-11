# Authentication

This tool uses LinkedIn OAuth bearer tokens in a controlled way.

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
