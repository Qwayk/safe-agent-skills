# AssetGenerationService (Google Ads API v25)

Command shape:
- `google-ads-api-tool asset-generation-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-images` — `AssetGenerationService.GenerateImages` (read; unary_unary) — request: `GenerateImagesRequest` → response: `GenerateImagesResponse`
- `generate-text` — `AssetGenerationService.GenerateText` (read; unary_unary) — request: `GenerateTextRequest` → response: `GenerateTextResponse`
