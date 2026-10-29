# CustomerManagerLinkService (Google Ads API v25)

Command shape:
- `google-ads-api-tool customer-manager-link-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `move-manager-link` — `CustomerManagerLinkService.MoveManagerLink` (write; plan-first; unary_unary) — request: `MoveManagerLinkRequest` → response: `MoveManagerLinkResponse`
- `mutate-customer-manager-link` — `CustomerManagerLinkService.MutateCustomerManagerLink` (write; plan-first; unary_unary) — request: `MutateCustomerManagerLinkRequest` → response: `MutateCustomerManagerLinkResponse`
