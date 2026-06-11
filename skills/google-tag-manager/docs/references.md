# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Google Tag Manager API v2 (Google)
- API docs home: https://developers.google.com/tag-platform/tag-manager/api/v2
- REST reference: https://developers.google.com/tag-platform/tag-manager/api/reference/rest
- Discovery (canonical method list; pinned snapshot source): https://tagmanager.googleapis.com/$discovery/rest?version=v2
- Auth/scopes: https://developers.google.com/tag-platform/tag-manager/api/v2/authorization
- Limits/quotas: https://developers.google.com/tag-platform/tag-manager/api/v2/limits-quotas
- Errors: https://developers.google.com/tag-platform/tag-manager/api/v2/errors
- System parameters: https://cloud.google.com/apis/docs/system-parameters
- Last verified (UTC): 2026-03-02

## Other sources (only if needed)

- None.
