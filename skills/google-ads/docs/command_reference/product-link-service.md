# ProductLinkService (Google Ads API v25)

Command shape:
- `google-ads-api-tool product-link-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `create-product-link` — `ProductLinkService.CreateProductLink` (write; plan-first; unary_unary) — request: `CreateProductLinkRequest` → response: `CreateProductLinkResponse`
- `remove-product-link` — `ProductLinkService.RemoveProductLink` (write; plan-first; unary_unary) — request: `RemoveProductLinkRequest` → response: `RemoveProductLinkResponse`
