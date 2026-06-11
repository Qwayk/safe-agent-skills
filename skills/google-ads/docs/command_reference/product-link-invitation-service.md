# ProductLinkInvitationService (Google Ads API v22)

Command shape:
- `google-ads-api-tool product-link-invitation-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `create-product-link-invitation` — `ProductLinkInvitationService.CreateProductLinkInvitation` (write; unary) — request: `CreateProductLinkInvitationRequest` → response: `CreateProductLinkInvitationResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `remove-product-link-invitation` — `ProductLinkInvitationService.RemoveProductLinkInvitation` (write; unary) — request: `RemoveProductLinkInvitationRequest` → response: `RemoveProductLinkInvitationResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `update-product-link-invitation` — `ProductLinkInvitationService.UpdateProductLinkInvitation` (write; unary) — request: `UpdateProductLinkInvitationRequest` → response: `UpdateProductLinkInvitationResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
