# IdentityVerificationService (Google Ads API v25)

Command shape:
- `google-ads-api-tool identity-verification-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `get-identity-verification` — `IdentityVerificationService.GetIdentityVerification` (read; unary_unary) — request: `GetIdentityVerificationRequest` → response: `GetIdentityVerificationResponse`
- `start-identity-verification` — `IdentityVerificationService.StartIdentityVerification` (write; plan-first; unary_unary) — request: `StartIdentityVerificationRequest` → response: `Empty`
