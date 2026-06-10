# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Zendesk
- API docs home: https://developer.zendesk.com/api-reference/
- Ticketing (Support) API reference: https://developer.zendesk.com/api-reference/ticketing/introduction/
- Ticketing OpenAPI snapshot source (canonical for coverage): https://developer.zendesk.com/zendesk/oas.yaml
- Rate limits: https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/rate-limits/
- Snapshot fetched (UTC): 2026-03-05T08:05:04Z
- Snapshot Last-Modified header: Wed, 04 Mar 2026 12:48:51 GMT
- Snapshot SHA256: a983460788b975c89989a7853d14ea200f5761c8d7e72b6500b41a48fdf32856
- Last verified (UTC): 2026-03-05

## Other sources (only if needed)

(None)
