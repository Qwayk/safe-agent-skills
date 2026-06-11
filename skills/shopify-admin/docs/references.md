# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Shopify
- Admin GraphQL API home: https://shopify.dev/docs/api/admin-graphql
- Admin GraphQL API reference (pinned version 2026-01): https://shopify.dev/docs/api/admin-graphql/2026-01
- Admin GraphQL API full index (canonical inventory; pinned version 2026-01): https://shopify.dev/docs/api/admin-graphql/2026-01/full-index
  - Note (2026-03-04): Shopify currently redirects versioned URLs like `/2026-01/...` to `/latest/...`. The tool’s pinned-version inventory is derived from the committed snapshot under `docs/official_full_index_2026-01_2026-03-04.html`.
- API versioning policy: https://shopify.dev/docs/api/usage/versioning
- Rate limits: https://shopify.dev/docs/api/usage/rate-limits
- Admin API authentication / app auth: https://shopify.dev/docs/apps/auth
- Last verified (UTC): 2026-03-04

## Other sources (only if needed)

- None
