# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Mercury
- API docs home: https://docs.mercury.com/reference/
- Auth docs: https://docs.mercury.com/docs/getting-started
- Sandbox docs (base URL): https://docs.mercury.com/docs/using-mercury-sandbox
- Rate limits docs: Not found in official docs as-of 2026-01-29 (UTC)
- Last verified (UTC): 2026-01-29

## Other sources (only if needed)

- https://dash.readme.com/api/v1/api-registry/fgvdq2m4mkvj7lux — reason: public OpenAPI spec used to enumerate v1 endpoints and auth schemes — last verified (UTC): 2026-01-29
