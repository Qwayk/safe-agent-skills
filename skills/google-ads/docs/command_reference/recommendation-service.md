# RecommendationService (Google Ads API v22)

Command shape:
- `google-ads-api-tool recommendation-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `apply-recommendation` — `RecommendationService.ApplyRecommendation` (write; unary) — request: `ApplyRecommendationRequest` → response: `ApplyRecommendationResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `dismiss-recommendation` — `RecommendationService.DismissRecommendation` (read; unary) — request: `DismissRecommendationRequest` → response: `DismissRecommendationResponse`
- `generate-recommendations` — `RecommendationService.GenerateRecommendations` (read; unary) — request: `GenerateRecommendationsRequest` → response: `GenerateRecommendationsResponse`
