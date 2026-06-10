# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets in this file.
- When a capability depends on a specific documented behavior, link the exact doc page.

## Provider docs (official)

- Provider: Google Ads API
- Supported Google Ads API version: v22
- API docs home: https://developers.google.com/google-ads/api/docs/start
- Client library supported versions table: https://developers.google.com/google-ads/api/docs/client-libs
- Python client library: https://developers.google.com/google-ads/api/docs/client-libs/python
- OAuth / authentication: https://developers.google.com/google-ads/api/docs/oauth/overview
- GAQL (Google Ads Query Language): https://developers.google.com/google-ads/api/docs/query/overview
- Quotas / limits: https://developers.google.com/google-ads/api/docs/best-practices/quotas
- RPC reference (v22): https://developers.google.com/google-ads/api/reference/rpc/v22/overview
- Representative mutate request references (v22):
  - MutateGoogleAdsRequest: https://developers.google.com/google-ads/api/reference/rpc/v22/MutateGoogleAdsRequest
  - MutateCampaignsRequest: https://developers.google.com/google-ads/api/reference/rpc/v22/MutateCampaignsRequest
  - MutateCustomerRequest: https://developers.google.com/google-ads/api/reference/rpc/v22/MutateCustomerRequest
- Last verified (UTC): 2026-03-02

## Implementation-derived references (reproducible)

- RPC surface snapshots (v22; committed; enforced by unit tests):
  - Official surface: curated from the official v22 RPC reference and committed as `docs/official_rpc_surface_v22_2026-03-01.txt`.
  - Client surface: derived from the pinned `google-ads` python package (29.2.0) and committed as `docs/client_rpc_surface_v22_2026-03-01.txt`.
  - CLI surface: derived from the tool registry and committed as `docs/cli_rpc_surface_v22_2026-03-01.txt`.
