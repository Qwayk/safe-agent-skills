# Agent recipes (question → preset → commands → tables)

These recipes are designed so an AI agent can work without knowing GAQL.

Important safety rules:
- Never ask the user to paste secrets into chat.
- Dry-run first, then apply only with explicit user approval.
- Snapshot exports are read-only to Google Ads, but they can consume quota and write local files.

## Investigate a specific account question

Use direct GAQL to retrieve relevant evidence, or select a preset when a saved pack is useful. No export or diagnosis sequence is required. For example:

```bash
google-ads-api-tool --output json gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT campaign.id, campaign.name, campaign.status FROM campaign"
```

Omit `--limit` for complete query results. `meta.limited` means the client cap omitted rows; GAQL LIMIT still narrows the requested dataset. `--page-size` is ignored and retained for compatibility. Verify customer identity, account timezone, closed date windows, conversion delay and completeness before interpreting performance.

Choose the fields that answer the question. For delivery, examine configuration, daily performance and budget/rank constraints; for ad quality, inspect query/ad/page fit and actual outcomes; for conversions, examine actions and each campaign's standard and custom goals. Primary/Secondary labels alone do not establish effective campaign bidding goals. Recommendations and platform quality labels do not prove causality.

## Optional export packs

Use `presets list` and `presets show` to choose useful datasets. `optimization_pack_v1`, `analysis_pack_v2` and `analysis_pack_max_v1` remain available. Preview the export, then use `--apply --yes` for the authorized local export. Inspect the manifest for missing, failed or truncated tables before using them. Read the underlying evidence and choose research questions yourself.

The `snapshot analyze diagnose` and `optimize` commands are legacy heuristic reports retained for compatibility. Their fixed thresholds, goal interpretation and impression-share aggregation are not verified advertising judgment; they are not a prerequisite or the default investigation path. See [diagnosis reference](diagnosis_reference.md) for the retained command schema.

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

Use GAQL directly:
- discover fields: `google-ads-api-tool fields search --contains campaign`
- use a small limit to explore the field shape; omit limits for complete evidence:
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
