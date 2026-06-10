# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth / refresh tokens

- If you see auth failures, re-check your `.env` values and run `google-ads-api-tool onboarding` to confirm which keys are missing.
- If your refresh token is revoked/expired, generate a new refresh token (per Google Ads API docs) and update `GOOGLE_ADS_REFRESH_TOKEN` in `.env`.

## Snapshot export: “output explosion” and quotas

Snapshot export can return a lot of rows quickly (especially when you export long date ranges).

Safer defaults:
- Start with a shorter date range first (example: 7 days) and verify table shapes.
- Prefer presets (bounded) over ad-hoc GAQL.

Explosion controls:
- Use `--max-rows N` to cap rows per query group. The manifest records `truncated=true` and adds a warning when a cap is hit.
- Use a smaller `--page-size` (example: 500) if you hit transient API issues (slower but sometimes more stable).

## Snapshot analyze diagnose: missing finding families

- `snapshot analyze diagnose` only reports families supported by the exported tables.
- If `tables_missing` includes `campaign_pressure_daily`, `keyword_quality_snapshot`, `conversion_actions`, or `recommendations`, export `optimization_pack_v1` instead of reusing an older pack.
- If `tables_missing` includes `rsa_asset_performance`, `landing_pages_daily`, or `placements_daily`, re-export with `--include-optional`.

## Snapshot analyze diagnose: why did I only get a few findings?

- The thresholds are intentionally conservative in v1.
- Low-volume packs may return only `low_volume_or_targeting_limited` or no findings at all.
- The report is offline-only and descriptive. It is not trying to force every entity into a recommendation.
- `quality_score_issue` now skips rows with no real signal. If you expected more QS findings, inspect `tables/keyword_quality_snapshot.jsonl` for rows that still have almost no traffic.

## Snapshot analyze diagnose: docs versus books routing

- Check `findings[].support_route` before you query support material.
- `google_ads_docs` means the official Google Ads docs lane should help.
- `books_or_human` means the finding needs judgment, not just current platform mechanics.

## Snapshot export: temp audit without client run-history writes

- Add `--no-artifacts` when you want a real export pack but do not want local run-history files written beside the env file.
- If your env file lives under a client `.state/` folder and you do want artifacts, run history now stays under that same `.state/runs/` path.

## Snapshot analyze diagnose: recommendation findings

- `recommendation_review` is review-only by design.
- If you need to inspect or apply native Google recommendations, use the explicit `recommendation-service` commands after human review.
- Do not treat optimization score or recommendation count as permission to auto-apply anything.

## Snapshot export: partial success vs strict mode

- Default behavior is partial success: if a group fails, export continues, and the error is recorded in `errors/errors.jsonl` and reflected in `manifest.json`.
- Use `--strict` if you require a complete pack: exit code is 1 when any required group fails (pack artifacts are still written for auditability).

## Permissions and customer access

- If `customers list-accessible` returns 0 customers, you may be authenticated but lack access.
- If you see permission errors on export, verify the `--customer-id` is one of the accessible customers and that your OAuth user has the needed access in Google Ads.

## Write RPC refusals (expected safety behavior)

If an RPC write command returns `refused=true`, it is enforcing safety gates.
Common causes:
- Missing `--apply` (default is plan-only for writes)
- Customer id is not in `GOOGLE_ADS_WRITE_CUSTOMER_ID_ALLOWLIST` (default deny)
- Global kill switch enabled (`GOOGLE_ADS_EXTERNAL_WRITES_DISABLED=1`)
- Missing `--yes` for risky/batch operations
- Missing `--ack-spend` for budget/billing/spend-impacting operations
- Missing `--ack-irreversible` for remove operations
- Missing `--ack-sensitive-payload` when using `--include-rpc-payload` (raw payloads may contain sensitive data)
- High-risk operation missing `--plan-in` (plan drift protection)

## Write receipts: `ok` versus `fully_verified`

- `verification.ok=true` means the tool did not find a mismatch in read-back.
- `verification.fully_verified=true` means it also checked every update field it safely could.
- If `verification.ok=true` but `verification.fully_verified=false`, inspect `verification.skipped_fields`.
- Common skip reasons:
  - the update mask pointed to a field that was not present in the update payload
  - GAQL did not return the field in a safe way the tool could prove

## Builder specs: validation errors

- If a builder says a required key is missing, compare your spec to the example files in `docs/examples/inputs/`.
- Search and competitor builders need: `customer_id`, `budget`, `campaign`, `targeting`, and `ad_groups`.
- DSA feed builder also needs: `page_feed`, `ad_group`, `ad`, and `webpage_target`.
- Competitor builder only allows `EXACT` positive keywords.

## Builder applies: why am I still getting `--ack-spend` or `--plan-in` errors?

- Builders compile one `GoogleAdsService.Mutate` request, but the safety checks still inspect the inner operations.
- If the spec creates or updates budgets, you still need `--ack-spend`.
- If the compiled request is high-risk, you still need `--plan-in`.
- Builder creates are not the current live-change path yet. Use reviewed RPC/helper writes for live work until builders have snapshot support or explicit no-snapshot approval support.
