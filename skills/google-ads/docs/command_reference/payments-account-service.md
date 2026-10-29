# PaymentsAccountService (Google Ads API v25)

Command shape:
- `google-ads-api-tool payments-account-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `list-payments-accounts` — `PaymentsAccountService.ListPaymentsAccounts` (read; unary_unary) — request: `ListPaymentsAccountsRequest` → response: `ListPaymentsAccountsResponse`
