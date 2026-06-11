# Authentication

## 1) Access token in `.env`

Put these values in `.env`:

- `TIKTOK_MARKETING_APP_ID`
- `TIKTOK_MARKETING_APP_SECRET`
- `TIKTOK_MARKETING_ACCESS_TOKEN`

Then run:

```bash
tiktok-marketing-api-tool --output json auth check
```

The check validates credentials against `oauth2-advertiser-get`.

If you want the official token exchange endpoint itself, it is also shipped as:

```bash
tiktok-marketing-api-tool --output json api ops show --op oauth2-access-token
```

The live token exchange endpoint is a POST operation, so apply follows the same write gates and requires explicit no-snapshot approval when no useful saved snapshot is available:
`--live --apply --yes --plan-in plan.json --ack-irreversible`.

## 2) OAuth token JSON (manual)

If you use token file auth:

1) Put token JSON into your token file path:

```bash
tiktok-marketing-api-tool --output json auth token set --file token.json
```

2) Confirm the token file is present:

```bash
tiktok-marketing-api-tool --output json auth token status
```

3) Run auth check:

```bash
tiktok-marketing-api-tool --output json auth check
```

`auth check` uses `.state/token.json` only when `TIKTOK_MARKETING_ACCESS_TOKEN` is missing.

### Notes

- Never print secrets.
- Do not store app secrets in logs or chat.
- `auth check` is a live read-only call, not a local-only placeholder.
