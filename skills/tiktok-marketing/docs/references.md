# References (sources)

## Official references

- Provider: TikTok for Business Marketing API
- API docs home: `https://ads.tiktok.com/marketing_api/docs`
- Portal docs home: `https://business-api.tiktok.com/portal/docs`
- Auth reference: `https://business-api.tiktok.com/portal/docs?id=1738455508553729`
- TikTok official SDK source: `https://github.com/tiktok/tiktok-business-api-sdk`

## Runtime manifest source

- Pinned manifest file: `docs/official_operations_v1_2026-05-24.json`
- Manifest generated at (UTC): `2026-05-24T07:01:08Z`
- Union operation count: `240`
- Source commit used for generation: `f809c396520df2d7b201a9ccc5378d822b728ed3`
- Last verified this doc: `2026-05-24`
- Runtime source precedence: official generated Python SDK first, then official `yml_files` rows for gaps.

## Known doc conflict handled by this tool

- Some official `yml_files` rows mark `Access-Token` like a query requirement.
- The official generated Python SDK sends `Access-Token` as a header.
- This tool follows the generated SDK request shape at runtime and keeps `app_id` / `secret` in query for `oauth2-advertiser-get`.

## Other sources

- SDK and endpoint docs linked from every operation via `api ops show --op <operation>`.
