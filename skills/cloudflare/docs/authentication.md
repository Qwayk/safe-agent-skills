# Authentication

This tool uses Cloudflare **API Tokens** (recommended by Cloudflare).

## How it works

- Header: `Authorization: Bearer <token>`
- Token is provided via `CLOUDFLARE_API_TOKEN` in your `--env-file` (usually `.env`).

This tool never prints your token and never logs auth headers.

## Smoke test

Run:

```bash
python3 -m cloudflare_api_tool --env-file .env --output json auth check
```

This calls `GET /user/tokens/verify` and returns the token status (but never the token value).

## Capability probe (recommended)

If `auth check` succeeds but later commands fail due to missing permissions, run:

```bash
python3 -m cloudflare_api_tool --env-file .env --output json auth probe
```

This performs a small set of read-only checks (no writes, no sensitive reads) and reports what your token can currently access.
