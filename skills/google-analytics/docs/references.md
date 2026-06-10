# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Google Analytics 4 (GA4)
- Analytics Admin API docs: https://developers.google.com/analytics/devguides/config/admin/v1
- Analytics Data API docs: https://developers.google.com/analytics/devguides/reporting/data/v1
- Auth overview (Google): https://cloud.google.com/docs/authentication
- Admin API quota management: https://developers.google.com/analytics/devguides/config/admin/v1/quota
- Data API quota management: https://developers.google.com/analytics/devguides/reporting/data/v1/quotas
- Google APIs system parameters: https://cloud.google.com/apis/docs/system-parameters
- Google API errors (design): https://cloud.google.com/apis/design/errors
- OAuth 2.0 (Google Identity): https://developers.google.com/identity/protocols/oauth2
- Last verified (UTC): 2026-03-03

## Discovery snapshots (canonical 100% lists)

These are the pinned lists used to define “100% coverage” for this tool:

- Analytics Admin API v1alpha discovery:
  - https://analyticsadmin.googleapis.com/$discovery/rest?version=v1alpha
- Analytics Data API v1beta discovery:
  - https://analyticsdata.googleapis.com/$discovery/rest?version=v1beta
- Analytics Data API v1alpha discovery (not currently served via the public discovery endpoint; vendored from Google’s API client repo):
  - https://analyticsdata.googleapis.com/$discovery/rest?version=v1alpha

## Other sources (only if needed)

- None.
