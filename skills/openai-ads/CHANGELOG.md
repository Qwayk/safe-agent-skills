# Changelog

## November 22, 2026

- Send each approved write once. Save a receipt if the result is unknown.
- Keep the chosen settings file in the next command, and include the skill and guides in the source download.
- Show event names and tracking windows in conversion settings while keeping private data hidden.
- Retire the old audience upload command and make two list filters optional to match the current API.
- Put setup, examples, and approvals in the existing guides.

## 0.1.0 - 2026-07-06

- Created the OpenAI Ads safe API CLI from the Python API tool template.
- Pinned the official OpenAI Ads OpenAPI spec and generated a 41-operation inventory.
- Added explicit generated commands for campaigns, ad groups, ads, ad account, insights, custom audiences, conversions, targeting, and file upload.
- Added manual measurement commands for JavaScript Pixel guidance, image tag building, supported events, and server-side Conversions API send planning.
- Added review-first writes, high-risk acknowledgements, no-snapshot approval, redaction, run artifacts, coverage docs, proof docs, examples, tests, and the `openai-ads` skill wrapper.
- Fixed governor review blockers by adding private Ads-field redaction across plans/logs/errors/run proof and body-aware high-risk detection for spend, serving, targeting, upload, audience, account, auth, and measurement fields.
