# Agent recipes (question → preset → commands → tables)

These recipes are designed so an AI agent can work without knowing GAQL.

Important safety rules:
- Never ask the user to paste secrets into chat.
- Dry-run first, then apply only with explicit user approval.
- Snapshot exports are read-only to Google Ads, but they can consume quota and write local files.

## Recipe: “Diagnose a Search account for optimization work”

Preset:
- `optimization_pack_v1`

Commands:
1) Dry-run:
   - `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --include-optional`
2) Apply (after approval):
   - `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes --include-optional`
3) Diagnose:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`
4) Temp implementation audit only:
   - `google-ads-api-tool --no-artifacts snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./tmp/google-ads-pack --apply --yes --include-optional`

Use this order after diagnose:
1) Read `findings[]`, `actions`, and `findings[].recommended_doc_queries`.
2) Run the exact docs queries from diagnose for the important mechanics questions.
3) Read only the tables tied to the active findings.
4) Check `findings[].support_route` before choosing docs versus books.
5) Use `analysis_pack_max_v1` only if the pack is missing needed tables.
6) Use GAQL only if the needed field is still missing.

Core tables to read first:
- `manifest.json` (warnings, truncation, and which groups failed)
- `tables/campaign_pressure_daily.jsonl`
- `tables/keyword_quality_snapshot.jsonl`
- `tables/conversion_actions.jsonl`
- `tables/recommendations.jsonl`
- `tables/ad_daily_metrics.jsonl`

## Recipe: “Low impressions: budget vs rank vs low volume”

Preset:
- `optimization_pack_v1`

Commands:
1) Export the pack.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` where `category` is one of:
  - `budget_pressure`
  - `rank_pressure`
  - `mixed_pressure`
  - `low_volume_or_targeting_limited`

Next:
- run the exact `recommended_doc_queries` from those findings
- then inspect `tables/campaign_pressure_daily.jsonl`
- for rank issues, add `tables/keyword_quality_snapshot.jsonl` and `tables/ad_daily_metrics.jsonl`

## Recipe: “Fix RSA strength”

Preset:
- `optimization_pack_v1`

Commands:
1) Export with `--include-optional` so RSA asset labels are present.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` with `category = rsa_issue`
- `tables/ad_group_ads.jsonl`
- `tables/ad_daily_metrics.jsonl`
- `tables/rsa_asset_performance.jsonl`

## Recipe: “Quality Score diagnosis”

Preset:
- `optimization_pack_v1`

Commands:
1) Export the pack.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` with `category = quality_score_issue`
- `tables/keyword_quality_snapshot.jsonl`
- `tables/search_terms_daily.jsonl`
- `tables/landing_pages_daily.jsonl` when present

## Recipe: “Recommendation review without auto-apply”

Preset:
- `optimization_pack_v1`

Commands:
1) Export the pack.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` with `category = recommendation_review`
- `tables/recommendations.jsonl`
- `tables/customer_overview.jsonl`
- `tables/campaign_inventory.jsonl`

Rule:
- recommendations are review-only in this workflow
- do not auto-apply anything from the diagnose output

## Recipe: “Pause or keep this keyword?”

Preset:
- `optimization_pack_v1`

Commands:
1) Export the pack.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` with `category = keyword_pause_candidate`

Rule:
- if `support_route` is `books_or_human`, do not treat Google Help as the answer source
- use books or human review for the final pause-or-keep judgment

## Recipe: “Zero conversions: tracking risk first”

Preset:
- `optimization_pack_v1`

Commands:
1) Export the pack.
2) Run:
   - `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

Read:
- `findings[]` with `category = tracking_risk`
- `tables/conversion_actions.jsonl`
- `tables/ad_daily_metrics.jsonl`
- `tables/ad_daily_conversions_by_action.jsonl` when present

## Recipe: “Deepen a finding after diagnose”

Rule:
- use diagnose output as the control plane
- do not start with ad hoc table slicing
- do not widen to `analysis_pack_max_v1` unless the first pack is missing needed data

Finding to next tables:
- `rank_pressure`
  - `tables/campaign_pressure_daily.jsonl`
  - `tables/keyword_quality_snapshot.jsonl`
  - `tables/ad_daily_metrics.jsonl`
- `quality_score_issue`
  - `tables/keyword_quality_snapshot.jsonl`
  - `tables/search_terms_daily.jsonl`
  - `tables/landing_pages_daily.jsonl` when present
- `rsa_issue`
  - `tables/ad_group_ads.jsonl`
  - `tables/ad_daily_metrics.jsonl`
  - `tables/rsa_asset_performance.jsonl` when present
- `search_term_cleanup`
  - `tables/search_terms_daily.jsonl`
  - `tables/keyword_daily_metrics.jsonl`
- `tracking_risk`
  - `tables/conversion_actions.jsonl`
  - `tables/ad_daily_metrics.jsonl`
  - `tables/ad_daily_conversions_by_action.jsonl` when present
- `landing_page_review`
  - `tables/landing_pages_daily.jsonl`
  - `tables/search_terms_daily.jsonl`
- `placement_review`
  - `tables/placements_daily.jsonl`
- `recommendation_review`
  - `tables/recommendations.jsonl`
  - `tables/customer_overview.jsonl`
  - `tables/campaign_inventory.jsonl`

## Recipe: “Deep diagnosis fallback: placements + landing pages + conversion actions”

Preset:
- `analysis_pack_max_v1`

Commands:
1) Dry-run:
   - `google-ads-api-tool snapshot export --preset analysis_pack_max_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-max-pack --include-optional`
2) Apply (after approval):
   - `google-ads-api-tool snapshot export --preset analysis_pack_max_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-max-pack --apply --yes --include-optional`

Use this only after `optimization_pack_v1` plus diagnose if the original pack is missing the needed deeper tables.

Tables to read (examples; availability depends on the account):
- `tables/placements_daily.jsonl`
- `tables/landing_pages_daily.jsonl`
- `tables/ad_daily_conversions_by_action.jsonl`

## Recipe: “Explain why these 3 ads are winning”

Preset:
- `analysis_pack_v2`

Commands:
1) Dry-run:
   - `google-ads-api-tool snapshot export --preset analysis_pack_v2 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/winning-ads-pack --include-optional`
2) Apply (after approval):
   - `google-ads-api-tool snapshot export --preset analysis_pack_v2 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/winning-ads-pack --apply --yes --include-optional`

Tables to read:
- `tables/creative_anatomy.jsonl` (text + URL anatomy)
- `tables/ad_group_ads.jsonl` (ad type + status)
- `tables/campaigns.jsonl` and `tables/ad_groups.jsonl` (structure context)

## Recipe: “Compare two date ranges (descriptive diffs only)”

1) Export Pack A:
- `google-ads-api-tool snapshot export --preset analysis_pack_v2 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/pack_a --apply --yes --overwrite --include-optional`

2) Export Pack B:
- `google-ads-api-tool snapshot export --preset analysis_pack_v2 --customer-id YOUR_CUSTOMER_ID --since 2026-02-01 --until 2026-02-28 --out-dir ./out/pack_b --apply --yes --overwrite --include-optional`

3) Compare (dry-run → apply):
- `google-ads-api-tool snapshot compare --pack-a ./out/pack_a --pack-b ./out/pack_b --out-dir ./out/compare`
- `google-ads-api-tool snapshot compare --pack-a ./out/pack_a --pack-b ./out/pack_b --out-dir ./out/compare --apply --overwrite`

Read:
- `compare_summary.json` (descriptive diffs only; no causal claims)

## Recipe: “I need one weird field that the preset doesn’t include”

Use the preset export first (so you have a pack), then use GAQL for edge cases:
- discover fields: `google-ads-api-tool fields search --contains campaign`
- run a narrow GAQL query with a small `--limit`:
  - `google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT campaign.id, campaign.name FROM campaign LIMIT 5" --limit 5`

## Recipe: “Pause these reviewed keywords without hand-writing RPC JSON”

Prepare `keyword_pause_items.json`:
- resource names as strings, or
- objects with `ad_group_id` and `criterion_id`

Commands:
1) Dry-run:
   - `google-ads-api-tool helpers keywords pause-from-list --customer-id YOUR_CUSTOMER_ID --items ./keyword_pause_items.json`
2) Apply (after approval):
   - `google-ads-api-tool --apply --yes helpers keywords pause-from-list --customer-id YOUR_CUSTOMER_ID --items ./keyword_pause_items.json`

Check after apply:
- `verification.ok`
- `verification.fully_verified`
- `verification.skipped_fields`

## Recipe: “Change a budget or Maximize Clicks ceiling fast”

Dry-run:
- `google-ads-api-tool helpers campaign set-budget --customer-id YOUR_CUSTOMER_ID --budget-id YOUR_BUDGET_ID --amount 70`
- `google-ads-api-tool helpers campaign set-max-clicks-cpc-ceiling --customer-id YOUR_CUSTOMER_ID --campaign-id YOUR_CAMPAIGN_ID --amount 15`

Apply (after approval):
- add `--apply --yes --ack-spend`

Read the receipt:
- `verification.ok`
- `verification.fully_verified`

## Recipe: “Build a whole Search or DSA campaign safely”

Start from the example spec files:
- `docs/examples/inputs/builder_search_campaign_spec.json`
- `docs/examples/inputs/builder_competitor_search_spec.json`
- `docs/examples/inputs/builder_dsa_feed_search_spec.json`

Dry-run:
- `google-ads-api-tool builders search-campaign from-spec --spec ./docs/examples/inputs/builder_search_campaign_spec.json`
- `google-ads-api-tool builders dsa-feed-search from-spec --spec ./docs/examples/inputs/builder_dsa_feed_search_spec.json`

Apply after approval:
- add `--apply --yes`
- add `--ack-spend` if the build creates or changes budgets
- add `--plan-in` when the dry-run marked the build as high-risk

Check the run folder:
- `spec.json`
- `request.json`
- `builder_manifest.json`
- `plan.json`
- `receipt.json`
- `after.json`
