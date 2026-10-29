# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets in this file.
- When a capability depends on a specific documented behavior, link the exact doc page.

## Provider docs (official)

- Provider: Google Ads API
- Supported Google Ads API version: v25
- API docs home: https://developers.google.com/google-ads/api/docs/start
- Client library supported versions table: https://developers.google.com/google-ads/api/docs/client-libs
- Python client library: https://developers.google.com/google-ads/api/docs/client-libs/python
- OAuth / authentication: https://developers.google.com/google-ads/api/docs/oauth/overview
- GAQL (Google Ads Query Language): https://developers.google.com/google-ads/api/docs/query/overview
- Quotas / limits: https://developers.google.com/google-ads/api/docs/best-practices/quotas
- RPC reference (v25): https://developers.google.com/google-ads/api/reference/rpc/v25/overview
- Representative mutate request references (v25):
  - MutateGoogleAdsRequest: https://developers.google.com/google-ads/api/reference/rpc/v25/MutateGoogleAdsRequest
  - MutateCampaignsRequest: https://developers.google.com/google-ads/api/reference/rpc/v25/MutateCampaignsRequest
  - MutateCustomerRequest: https://developers.google.com/google-ads/api/reference/rpc/v25/MutateCustomerRequest
- Last verified (UTC): 2026-03-02

## Implementation-derived references (reproducible)

- RPC surface snapshots (v25; committed; enforced by unit tests):
  - Official surface: derived independently from Google’s official v25 protobuf service declarations and committed as `docs/official_rpc_surface_v25_2026-09-22.txt`.
  - Client surface: derived from the pinned `google-ads` python package (32.0.0) and committed as `docs/client_rpc_surface_v25_2026-09-22.txt`.
  - CLI surface: derived from the tool registry and committed as `docs/cli_rpc_surface_v25_2026-09-22.txt`.

- [Cloud project access and developer token sunset](https://developers.google.com/google-ads/api/docs/api-policy/developer-token) — checked 2026-09-22; tokens are no longer sent.
- [v25.1 release notes](https://developers.google.com/google-ads/api/docs/release-notes) — ACA and broad-match campaign migration dates.
