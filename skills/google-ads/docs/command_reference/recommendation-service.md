# RecommendationService (Google Ads API v25)

Command shape:
- `google-ads-api-tool recommendation-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `apply-recommendation` — `RecommendationService.ApplyRecommendation` (write; plan-first; unary_unary) — request: `ApplyRecommendationRequest` → response: `ApplyRecommendationResponse`
- `dismiss-recommendation` — `RecommendationService.DismissRecommendation` (write; plan-first; unary_unary) — request: `DismissRecommendationRequest` → response: `DismissRecommendationResponse`
- `generate-recommendations` — `RecommendationService.GenerateRecommendations` (read; unary_unary) — request: `GenerateRecommendationsRequest` → response: `GenerateRecommendationsResponse`
