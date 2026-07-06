# Changelog

## 0.1.0 - 2026-07-06

- Created the OpenAI Ads safe API CLI from the Python API tool template.
- Pinned the official OpenAI Ads OpenAPI spec and generated a 41-operation inventory.
- Added explicit generated commands for campaigns, ad groups, ads, ad account, insights, custom audiences, conversions, targeting, and file upload.
- Added manual measurement commands for JavaScript Pixel guidance, image tag building, supported events, and server-side Conversions API send planning.
- Added review-first writes, high-risk acknowledgements, no-snapshot approval, redaction, run artifacts, coverage docs, proof docs, examples, tests, and the `openai-ads` skill wrapper.
- Fixed governor review blockers by adding private Ads-field redaction across plans/logs/errors/run proof and body-aware high-risk detection for spend, serving, targeting, upload, audience, account, auth, and measurement fields.
