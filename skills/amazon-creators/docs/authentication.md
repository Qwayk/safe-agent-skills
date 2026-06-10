# Authentication

Amazon’s Creators Catalog API uses OAuth 2.0 credentials (credential ID, secret, version) plus a cached access token. This tool keeps secrets off the console and never prints raw tokens.

## Token storage

- Tokens live under `.state/token.json` next to your `.env` file.
- `amazon-creators-api-tool auth token fetch` now creates a dry-run plan. Confirmed apply requires explicit no-snapshot approval before token endpoint use or `.state/token.json` writes when no saved snapshot is available.
  - For v2.x credentials, the tool uses the Cognito token endpoint with a form-encoded request and `scope=creatorsapi/default`.
  - For v3.x credentials, the tool uses the LwA token endpoint with a JSON request and `scope=creatorsapi::default`.
- `amazon-creators-api-tool auth token set --file <token.json>` now creates a dry-run plan. Confirmed apply requires explicit no-snapshot approval before `.state/token.json` writes when no saved snapshot is available.
- `auth token status` reports the cached fields (exists, expiry, refresh token flag) without exposing the token value.

## Header construction

- The catalog commands read `.state/token.json` and build the `Authorization` header before calling the API. After trimming an optional leading `v`, versions that start with `2` get the `Version <credential_version>` suffix; other versions only send `Bearer <token>`.
- If the cache is missing or the token object lacks an `access_token`, you’ll see a `ValidationError` explaining that the token-cache helper can only plan and require approval when no saved snapshot is available.

## auth check

`auth check` ensures the cached token is valid (and not about to expire) in addition to verifying your env vars. If the cached token is missing or expired, the command fails with a `ValidationError` that points you toward the blocked token-fetch plan.

Recommended flow:

1. Create `.env` by hand from `.env.example`.
2. Use an existing local `.state/token.json` when available; token fetch/set commands currently plan and require approval before writing it.
3. Run `auth check` to confirm the env vars and cached token are healthy.
4. Run the catalog commands (`items get`, `browse-nodes describe`, etc.) and inspect the simplified outputs (use `--include-raw` when you need the raw payload).
