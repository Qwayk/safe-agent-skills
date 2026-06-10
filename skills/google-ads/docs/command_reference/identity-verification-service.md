# IdentityVerificationService (Google Ads API v22)

Command shape:
- `google-ads-api-tool identity-verification-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `get-identity-verification` — `IdentityVerificationService.GetIdentityVerification` (read; unary) — request: `GetIdentityVerificationRequest` → response: `GetIdentityVerificationResponse`
- `start-identity-verification` — `IdentityVerificationService.StartIdentityVerification` (read; unary) — request: `StartIdentityVerificationRequest` → response: `Empty`
