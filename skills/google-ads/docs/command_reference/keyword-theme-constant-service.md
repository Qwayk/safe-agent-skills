# KeywordThemeConstantService (Google Ads API v22)

Command shape:
- `google-ads-api-tool keyword-theme-constant-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `suggest-keyword-theme-constants` — `KeywordThemeConstantService.SuggestKeywordThemeConstants` (read; unary) — request: `SuggestKeywordThemeConstantsRequest` → response: `SuggestKeywordThemeConstantsResponse`
