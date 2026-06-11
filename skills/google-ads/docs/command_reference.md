# Command reference

Use this page when you need the exact Google Ads command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `google-ads-api-tool onboarding [--no-write-env]`

## Auth

- `google-ads-api-tool --output json --version`
- `google-ads-api-tool auth check`

## Customers

- `google-ads-api-tool customers list-accessible`

## GAQL

- `google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT customer.id FROM customer LIMIT 10"`
- `google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT campaign.id, campaign.name FROM campaign" --limit 5`

## Presets (GAQL templates)

- `google-ads-api-tool presets list`
- `google-ads-api-tool presets show --preset optimization_pack_v1`
- `google-ads-api-tool presets show --preset analysis_pack_v2`
- `google-ads-api-tool presets show --preset analysis_pack_max_v1`
- `google-ads-api-tool presets validate [--preset optimization_pack_v1]`

## Snapshot packs (analysis export)

Export writes a stable pack folder layout:
- `manifest.json`
- `tables/*.jsonl`
- `queries/queries.json`
- `errors/errors.jsonl`

Dry-run (no API calls, no pack writes):
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack`

Apply (read-only to Google Ads; writes local pack files):
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes`
- Snapshot files are analysis artifacts for local evidence. They are not a restore or rollback mechanism.
- Include optional preset groups: `--include-optional` (adds `required=false` groups; may increase time/quota)
- Temp implementation audits: add `--no-artifacts` if you want the pack but do not want local run-history files written beside the env file
- Optional explosion controls: `--max-rows 100000` and `--page-size 1000`
- Strict mode: `--strict` (fails if any required query group fails; pack still written for auditability)

Compare two packs (descriptive diffs only; no causal claims):

Dry-run (no writes):
- `google-ads-api-tool snapshot compare --pack-a ./out/pack_a --pack-b ./out/pack_b --out-dir ./out/compare`

Apply (writes compare summary JSON):
- `google-ads-api-tool snapshot compare --pack-a ./out/pack_a --pack-b ./out/pack_b --out-dir ./out/compare --apply --overwrite`

## Snapshot analysis (offline; pack → findings)

Primary workflow:
- `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

`diagnose` is read-only and returns a stable JSON report with:
- `summary`
- `data_quality`
- `tables_used`
- `tables_missing`
- `findings`
- `actions`
- `notes`

See `docs/diagnosis_reference.md` for the finding schema and built-in categories.
Important routing note:
- `findings[].support_route = google_ads_docs` means the official docs lane is the right support source.
- `findings[].support_route = books_or_human` means the finding needs durable judgment, not just Google Help mechanics.

Legacy best-effort optimization report:
- `google-ads-api-tool snapshot analyze optimize --pack-dir ./out/google-ads-pack`

For best results with the legacy report, export a deep pack first (includes search terms, keywords, landing pages, placements):
- `google-ads-api-tool snapshot export --preset analysis_pack_max_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes --include-optional --overwrite`

Tuning flags (optional):
- `--top-n N` (default: 50)
- Candidate negatives thresholds:
  - `--min-negative-cost-micros N` (default: 5000000)
  - `--min-negative-clicks N` (default: 3)
  - `--min-negative-impressions N` (default: 100)

## Fields (schema discovery)

- `google-ads-api-tool fields search --contains campaign`
- `google-ads-api-tool fields search --query "SELECT name, data_type WHERE name LIKE 'campaign.%'"`

## Helpers (common write jobs, less JSON by hand)

These helpers still use the same safety gates as normal write RPCs:
- dry-run first unless you pass `--apply`
- allowlist + kill switch still apply
- supported update operations and readable `CampaignCriterion` ad-schedule removes save before-state under `.state/runs/<run_id>/before/` before mutating
- create/upload-style helpers and unreadable removes need explicit no-snapshot approval support or a true blocker reason before live apply
- use `--yes`, `--ack-spend`, `--ack-irreversible`, and `--plan-in` when the risk level requires them

Commands:
- `google-ads-api-tool helpers keywords pause-from-list --customer-id YOUR_CUSTOMER_ID --items ./keyword_pause_items.json`
- `google-ads-api-tool helpers keywords add-from-list --customer-id YOUR_CUSTOMER_ID --ad-group-id YOUR_AD_GROUP_ID --items ./keyword_add_items.json`
- `google-ads-api-tool helpers campaign-negatives add-from-list --customer-id YOUR_CUSTOMER_ID --campaign-id YOUR_CAMPAIGN_ID --items ./campaign_negative_items.json`
- `google-ads-api-tool helpers campaign set-budget --customer-id YOUR_CUSTOMER_ID --budget-id YOUR_BUDGET_ID --amount 70`
- `google-ads-api-tool helpers campaign set-max-clicks-cpc-ceiling --customer-id YOUR_CUSTOMER_ID --campaign-id YOUR_CAMPAIGN_ID --amount 15`
- `google-ads-api-tool helpers entities lookup-by-name --customer-id YOUR_CUSTOMER_ID --resource-type campaign --name "Main Search"`
- `google-ads-api-tool helpers entities pause --customer-id YOUR_CUSTOMER_ID --resource-type campaign --items ./campaign_items.json`
- `google-ads-api-tool helpers entities enable --customer-id YOUR_CUSTOMER_ID --resource-type ad-group-ad --items ./ad_items.json`
- `google-ads-api-tool helpers campaign-tree pause --customer-id YOUR_CUSTOMER_ID --campaign-name "Main Search" --include-ad-groups --include-ads`
- `google-ads-api-tool helpers campaign-tree enable --customer-id YOUR_CUSTOMER_ID --campaign-id YOUR_CAMPAIGN_ID --include-ad-groups`
- `google-ads-api-tool helpers precheck overlap --customer-id YOUR_CUSTOMER_ID`
- `google-ads-api-tool helpers precheck policy-risk --items ./keywords_or_negatives.json`
- `google-ads-api-tool helpers offline upload-click-conversions --customer-id YOUR_CUSTOMER_ID --items ./click_conversions.json`

Accepted item file shapes:
- list of strings
- list of objects
- object with `items: [...]`
- `upload-click-conversions` also accepts `conversions: [...]`
- `.csv` files are accepted too for helper item inputs when the command uses `--items`

Common CSV columns:
- keyword pauses or entity batches: `resource_name`
- keyword adds or negatives: `text` plus optional `campaign_id`, `ad_group_id`, `match_type`, `status`
- click conversions: one row per conversion with the normal JSON field names as CSV headers

Examples:

`keyword_pause_items.json`
```json
[
  "customers/1234567890/adGroupCriteria/111~222",
  {"ad_group_id": "333", "criterion_id": "444"}
]
```

`keyword_add_items.json`
```json
[
  "sliding door roller repair dallas",
  {"text": "patio door wheel repair dallas", "match_type": "PHRASE"},
  {"text": "sliding glass door track repair", "match_type": "EXACT", "status": "PAUSED"}
]
```

`campaign_negative_items.json`
```json
[
  "glass repair",
  {"text": "screen replacement", "match_type": "PHRASE"},
  {"campaign_id": "777", "text": "buy parts", "match_type": "EXACT"}
]
```

`campaign_items.json`
```json
[
  "123456",
  {"resource_name": "customers/1234567890/campaigns/999999"}
]
```

`campaign_items.csv`
```csv
resource_name
customers/1234567890/campaigns/999999
```

`ad_items.json`
```json
[
  {"ad_group_id": "111", "ad_id": "222"},
  {"resource_name": "customers/1234567890/adGroupAds/333~444"}
]
```

`click_conversions.json`
```json
[
  {
    "gclid": "abc123",
    "conversion_action": "customers/1234567890/conversionActions/777",
    "conversion_date_time": "2026-05-22 10:00:00-05:00",
    "conversion_value": 1.0,
    "currency_code": "USD",
    "order_id": "row-1"
  }
]
```

Name lookups:
- supported resource types: `campaign`, `ad-group`, `campaign-budget`, `conversion-action`
- default match mode is `exact`
- use `--match contains` only when you expect multiple candidates and want to inspect them first

Campaign-tree helper:
- updates the campaign first
- add `--include-ad-groups` to update child ad groups too
- add `--include-ads` to update ads under those ad groups too
- it compiles one strict `GoogleAdsService.Mutate` request, so the normal write gates still apply
- because it is update-only, live apply can run when every target can be pre-read and before-state can be saved

Precheck helpers:
- `precheck overlap` is read-only and reports positive keyword overlap across campaigns
- `precheck policy-risk` is read-only and flags risky themes like locksmith, lockout, glass-replacement, screen-only, parts-buyer, and DIY intent

## Builders (whole campaign builds from strict spec files)

These builders compile one deterministic `GoogleAdsService.Mutate` request.
They use the same safety gates as other writes:
- dry-run first unless you pass `--apply`
- allowlist + kill switch still apply
- budget and other spend-impacting builds still require `--ack-spend`
- batch or high-risk applies still require `--yes`
- high-risk applies still require `--plan-in`
- builder creates are not the current live-change path; use reviewed RPC/helper writes for live work until builders have snapshot support or explicit no-snapshot approval support

Commands:
- `google-ads-api-tool builders search-campaign from-spec --spec ./docs/examples/inputs/builder_search_campaign_spec.json`
- `google-ads-api-tool builders competitor-search from-spec --spec ./docs/examples/inputs/builder_competitor_search_spec.json`
- `google-ads-api-tool builders dsa-feed-search from-spec --spec ./docs/examples/inputs/builder_dsa_feed_search_spec.json`

What they write when artifacts are enabled:
- `spec.json`
- `request.json`
- `builder_manifest.json`
- `plan.json`
- `receipt.json`
- `after.json`
- `README.md`

Search / competitor spec shape:
- required keys: `customer_id`, `budget`, `campaign`, `targeting`, `ad_groups`
- optional keys: `campaign_negatives`, `asset_creates`, `campaign_asset_links`, `cross_campaign_negatives`
- competitor builder rule: positive keywords must all be `EXACT`

DSA feed spec shape:
- required keys: `customer_id`, `budget`, `campaign`, `targeting`, `page_feed`, `ad_group`, `ad`, `webpage_target`
- optional keys: `campaign_negatives`, `cross_campaign_negatives`
- DSA builder rule: it sets `use_supplied_urls_only=true` and targets the page-feed label only

Example specs:
- `docs/examples/inputs/builder_search_campaign_spec.json`
- `docs/examples/inputs/builder_competitor_search_spec.json`
- `docs/examples/inputs/builder_dsa_feed_search_spec.json`

## Runs (history)

This tool supports reads + writes to Google Ads, and it can also write local artifacts (example: `snapshot export`). The `runs` commands show local run summaries for write-capable commands.

- `google-ads-api-tool runs list [--limit 20]`
- `google-ads-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`
- If your env file lives under a client `.state/` folder, run history now stays under that same client `.state/runs/` path.

## RPC methods (explicit per-service, per-method)

This tool exposes one explicit CLI command per official Google Ads API v22 RPC method.

Command shape:
- `google-ads-api-tool <service-kebab> <method-kebab> --in PATH.json`

Write behavior (safe-by-default):
- Without `--apply`, write methods emit a deterministic plan object (`dry_run=true`).
- With `--apply`, supported update operations and readable `CampaignCriterion` ad-schedule removes save before-state when possible, then require the normal safety gates (allowlist, kill switch, risk flags). See `docs/safety_model.md`.
- Create, upload, unreadable removes, and other unsupported write shapes need explicit no-snapshot approval support or a true blocker reason before live apply.
- Apply receipts now show both:
  - `verification.ok`
  - `verification.fully_verified`
- Plans and receipts now also include `plain_english_summary`
- Apply output and receipts include `before_state` for supported live writes.
- Readable ad-schedule remove receipts also include `restore_recipes`.
- If `verification.fully_verified=false`, inspect `verification.skipped_fields` before treating the change as fully proven.

Write-safety flags (global; can appear before or after subcommands):
- `--apply` (opt-in to external mutation)
- `--yes` (required for risky/batch writes)
- `--plan-out PATH.json` (write plan artifact)
- `--plan-in PATH.json` (apply from a reviewed plan; drift-checked)
- `--receipt-out PATH.json` (write an apply receipt artifact)
- `--ack-spend` (required for budget/billing/spend-impacting writes)
- `--ack-irreversible` (required for irreversible actions, like removals)
- `--include-rpc-payload --ack-sensitive-payload` (include raw RPC request/response payloads in plan/receipt outputs; sensitive)
- `--artifacts-dir PATH` (override the run folder used for plan/receipt/proof files)

Per-service reference pages:
- See `docs/command_reference/` (one page per service).

## RPC services index

One page per Google Ads API v22 RPC service:

- `account-budget-proposal-service` → `docs/command_reference/account-budget-proposal-service.md`
- `account-link-service` → `docs/command_reference/account-link-service.md`
- `ad-group-ad-label-service` → `docs/command_reference/ad-group-ad-label-service.md`
- `ad-group-ad-service` → `docs/command_reference/ad-group-ad-service.md`
- `ad-group-asset-service` → `docs/command_reference/ad-group-asset-service.md`
- `ad-group-asset-set-service` → `docs/command_reference/ad-group-asset-set-service.md`
- `ad-group-bid-modifier-service` → `docs/command_reference/ad-group-bid-modifier-service.md`
- `ad-group-criterion-customizer-service` → `docs/command_reference/ad-group-criterion-customizer-service.md`
- `ad-group-criterion-label-service` → `docs/command_reference/ad-group-criterion-label-service.md`
- `ad-group-criterion-service` → `docs/command_reference/ad-group-criterion-service.md`
- `ad-group-customizer-service` → `docs/command_reference/ad-group-customizer-service.md`
- `ad-group-label-service` → `docs/command_reference/ad-group-label-service.md`
- `ad-group-service` → `docs/command_reference/ad-group-service.md`
- `ad-parameter-service` → `docs/command_reference/ad-parameter-service.md`
- `ad-service` → `docs/command_reference/ad-service.md`
- `asset-generation-service` → `docs/command_reference/asset-generation-service.md`
- `asset-group-asset-service` → `docs/command_reference/asset-group-asset-service.md`
- `asset-group-listing-group-filter-service` → `docs/command_reference/asset-group-listing-group-filter-service.md`
- `asset-group-service` → `docs/command_reference/asset-group-service.md`
- `asset-group-signal-service` → `docs/command_reference/asset-group-signal-service.md`
- `asset-service` → `docs/command_reference/asset-service.md`
- `asset-set-asset-service` → `docs/command_reference/asset-set-asset-service.md`
- `asset-set-service` → `docs/command_reference/asset-set-service.md`
- `audience-insights-service` → `docs/command_reference/audience-insights-service.md`
- `audience-service` → `docs/command_reference/audience-service.md`
- `automatically-created-asset-removal-service` → `docs/command_reference/automatically-created-asset-removal-service.md`
- `batch-job-service` → `docs/command_reference/batch-job-service.md`
- `bidding-data-exclusion-service` → `docs/command_reference/bidding-data-exclusion-service.md`
- `bidding-seasonality-adjustment-service` → `docs/command_reference/bidding-seasonality-adjustment-service.md`
- `bidding-strategy-service` → `docs/command_reference/bidding-strategy-service.md`
- `billing-setup-service` → `docs/command_reference/billing-setup-service.md`
- `brand-suggestion-service` → `docs/command_reference/brand-suggestion-service.md`
- `campaign-asset-service` → `docs/command_reference/campaign-asset-service.md`
- `campaign-asset-set-service` → `docs/command_reference/campaign-asset-set-service.md`
- `campaign-bid-modifier-service` → `docs/command_reference/campaign-bid-modifier-service.md`
- `campaign-budget-service` → `docs/command_reference/campaign-budget-service.md`
- `campaign-conversion-goal-service` → `docs/command_reference/campaign-conversion-goal-service.md`
- `campaign-criterion-service` → `docs/command_reference/campaign-criterion-service.md`
- `campaign-customizer-service` → `docs/command_reference/campaign-customizer-service.md`
- `campaign-draft-service` → `docs/command_reference/campaign-draft-service.md`
- `campaign-goal-config-service` → `docs/command_reference/campaign-goal-config-service.md`
- `campaign-group-service` → `docs/command_reference/campaign-group-service.md`
- `campaign-label-service` → `docs/command_reference/campaign-label-service.md`
- `campaign-lifecycle-goal-service` → `docs/command_reference/campaign-lifecycle-goal-service.md`
- `campaign-service` → `docs/command_reference/campaign-service.md`
- `campaign-shared-set-service` → `docs/command_reference/campaign-shared-set-service.md`
- `content-creator-insights-service` → `docs/command_reference/content-creator-insights-service.md`
- `conversion-action-service` → `docs/command_reference/conversion-action-service.md`
- `conversion-adjustment-upload-service` → `docs/command_reference/conversion-adjustment-upload-service.md`
- `conversion-custom-variable-service` → `docs/command_reference/conversion-custom-variable-service.md`
- `conversion-goal-campaign-config-service` → `docs/command_reference/conversion-goal-campaign-config-service.md`
- `conversion-upload-service` → `docs/command_reference/conversion-upload-service.md`
- `conversion-value-rule-service` → `docs/command_reference/conversion-value-rule-service.md`
- `conversion-value-rule-set-service` → `docs/command_reference/conversion-value-rule-set-service.md`
- `custom-audience-service` → `docs/command_reference/custom-audience-service.md`
- `custom-conversion-goal-service` → `docs/command_reference/custom-conversion-goal-service.md`
- `custom-interest-service` → `docs/command_reference/custom-interest-service.md`
- `customer-asset-service` → `docs/command_reference/customer-asset-service.md`
- `customer-asset-set-service` → `docs/command_reference/customer-asset-set-service.md`
- `customer-client-link-service` → `docs/command_reference/customer-client-link-service.md`
- `customer-conversion-goal-service` → `docs/command_reference/customer-conversion-goal-service.md`
- `customer-customizer-service` → `docs/command_reference/customer-customizer-service.md`
- `customer-label-service` → `docs/command_reference/customer-label-service.md`
- `customer-lifecycle-goal-service` → `docs/command_reference/customer-lifecycle-goal-service.md`
- `customer-manager-link-service` → `docs/command_reference/customer-manager-link-service.md`
- `customer-negative-criterion-service` → `docs/command_reference/customer-negative-criterion-service.md`
- `customer-service` → `docs/command_reference/customer-service.md`
- `customer-sk-ad-network-conversion-value-schema-service` → `docs/command_reference/customer-sk-ad-network-conversion-value-schema-service.md`
- `customer-user-access-invitation-service` → `docs/command_reference/customer-user-access-invitation-service.md`
- `customer-user-access-service` → `docs/command_reference/customer-user-access-service.md`
- `customizer-attribute-service` → `docs/command_reference/customizer-attribute-service.md`
- `data-link-service` → `docs/command_reference/data-link-service.md`
- `experiment-arm-service` → `docs/command_reference/experiment-arm-service.md`
- `experiment-service` → `docs/command_reference/experiment-service.md`
- `geo-target-constant-service` → `docs/command_reference/geo-target-constant-service.md`
- `goal-service` → `docs/command_reference/goal-service.md`
- `google-ads-field-service` → `docs/command_reference/google-ads-field-service.md`
- `google-ads-service` → `docs/command_reference/google-ads-service.md`
- `identity-verification-service` → `docs/command_reference/identity-verification-service.md`
- `invoice-service` → `docs/command_reference/invoice-service.md`
- `keyword-plan-ad-group-keyword-service` → `docs/command_reference/keyword-plan-ad-group-keyword-service.md`
- `keyword-plan-ad-group-service` → `docs/command_reference/keyword-plan-ad-group-service.md`
- `keyword-plan-campaign-keyword-service` → `docs/command_reference/keyword-plan-campaign-keyword-service.md`
- `keyword-plan-campaign-service` → `docs/command_reference/keyword-plan-campaign-service.md`
- `keyword-plan-idea-service` → `docs/command_reference/keyword-plan-idea-service.md`
- `keyword-plan-service` → `docs/command_reference/keyword-plan-service.md`
- `keyword-theme-constant-service` → `docs/command_reference/keyword-theme-constant-service.md`
- `label-service` → `docs/command_reference/label-service.md`
- `local-services-lead-service` → `docs/command_reference/local-services-lead-service.md`
- `offline-user-data-job-service` → `docs/command_reference/offline-user-data-job-service.md`
- `payments-account-service` → `docs/command_reference/payments-account-service.md`
- `product-link-invitation-service` → `docs/command_reference/product-link-invitation-service.md`
- `product-link-service` → `docs/command_reference/product-link-service.md`
- `reach-plan-service` → `docs/command_reference/reach-plan-service.md`
- `recommendation-service` → `docs/command_reference/recommendation-service.md`
- `recommendation-subscription-service` → `docs/command_reference/recommendation-subscription-service.md`
- `remarketing-action-service` → `docs/command_reference/remarketing-action-service.md`
- `shareable-preview-service` → `docs/command_reference/shareable-preview-service.md`
- `shared-criterion-service` → `docs/command_reference/shared-criterion-service.md`
- `shared-set-service` → `docs/command_reference/shared-set-service.md`
- `smart-campaign-setting-service` → `docs/command_reference/smart-campaign-setting-service.md`
- `smart-campaign-suggest-service` → `docs/command_reference/smart-campaign-suggest-service.md`
- `third-party-app-analytics-link-service` → `docs/command_reference/third-party-app-analytics-link-service.md`
- `travel-asset-suggestion-service` → `docs/command_reference/travel-asset-suggestion-service.md`
- `user-data-service` → `docs/command_reference/user-data-service.md`
- `user-list-customer-type-service` → `docs/command_reference/user-list-customer-type-service.md`
- `user-list-service` → `docs/command_reference/user-list-service.md`

<!-- END RPC SERVICES INDEX -->
