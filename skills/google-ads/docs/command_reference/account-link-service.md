# AccountLinkService (Google Ads API v25)

Command shape:
- `google-ads-api-tool account-link-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `create-account-link` — `AccountLinkService.CreateAccountLink` (write; plan-first; unary_unary) — request: `CreateAccountLinkRequest` → response: `CreateAccountLinkResponse`
- `mutate-account-link` — `AccountLinkService.MutateAccountLink` (write; plan-first; unary_unary) — request: `MutateAccountLinkRequest` → response: `MutateAccountLinkResponse`
