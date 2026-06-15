# Authentication

Cloudflare authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because zones, DNS, Workers, routes, security settings, logs, and infrastructure can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Cloudflare environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

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
