# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: X (X API v2)
- OpenAPI snapshot URL (pinned): `https://api.x.com/2/openapi.json`
- OpenAPI “Important resources” (links the spec): `https://docs.x.com/x-api/getting-started/important-resources`
- OAuth2 (PKCE) endpoints (from pinned OpenAPI snapshot):
  - Authorization URL: `https://api.x.com/2/oauth2/authorize`
  - Token URL: `https://api.x.com/2/oauth2/token`
- Developer portal / docs home: `https://developer.x.com/`
- Key docs used by this tool:
  - Auth (OAuth2 Authorization Code + PKCE): `https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code`
  - Direct Messages (manage): `https://docs.x.com/x-api/direct-messages/manage/integrate`
  - Direct Messages (lookup): `https://docs.x.com/x-api/direct-messages/lookup/introduction`
  - Data dictionary (user field `receives_your_dm`): `https://docs.x.com/x-api/fundamentals/data-dictionary`
  - Rate limits: `https://docs.x.com/x-api/fundamentals/rate-limits`
  - Pricing: `https://docs.x.com/x-api/getting-started/pricing`
- Policy used by DM bulk safety checks:
  - X automation rules (Automated Direct Messages): `https://help.x.com/articles/20174732`
- Developer terms & policy:
  - `https://developer.x.com/en/developer-terms/agreement-and-policy.html`
- Snapshot integrity:
  - `docs/official_openapi_x_api_v2.json` sha256: `71944b1b618fff12d8dc1554f6f3276d3725e256e3aff6a22678a9d1f7e60162`
Last verified (UTC): 2026-03-01

## Other sources (only if needed)

- None.
