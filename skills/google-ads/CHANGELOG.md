# Changelog

## 0.7.3 — 2026-10-29

- Verify created keywords against their ordered mutation results: literal text, match type, positive/negative state, ad group and requested status. Presence-only or incomplete checks no longer report full verification. Remove-only absence checks and single-submission writes remain unchanged.
- GAQL uses one-row lookahead to distinguish an exact limit from omitted results.
- Retain `--page-size` as an ignored compatibility option and disclose this in metadata/help.
- Remove mandatory export/heuristic-diagnosis instructions; retain public commands and all live-write protections.

## 0.7.2 — 2026-09-22

- Preserve partial-failure receipts when protobuf error details are unknown or malformed. Decode known details independently and count undecoded details without exposing their bytes. Regression proof covers unknown, malformed, and mixed details, actual receipt files, and single submission.


## 0.7.1 — 2026-09-22

- Report partial failures with safe error locations and a nonzero exit status.
- Submit writes once, disable SDK retries, and record ambiguous transport failures with read-back evidence.
- Distinguish validated, verified, accepted-unverified, failed-verification, and unknown outcomes; no-target or capped verification is not full proof.
- Remove the developer-token requirement and header; document Cloud project API access.
- Include AI Max ACA/broad-match migration dates in campaign settings exports.
- Clarify mapped API coverage versus live-tested workflows.


## 0.7.0 — 2026-09-22

- Upgrade to Google Ads API v25 with v25.1 definitions in `google-ads==32.0.0`. All client defaults, explicit RPC calls, and request parsing now select v25.
- Refresh the explicit registry to 169 methods across 110 services, independently matched to Google's official protobuf declarations. Retire the two removed lifecycle-goal commands; keep the former Python registry import as a compatibility alias.
- Add the YouTube request-module naming exception and guard booking/authorization methods as writes; reservation operations receive spend-risk classification.
- Verify all 38 unique bundled GAQL templates with Google's validation-only API, account reads, and a validation-only campaign request. No campaign changes were applied.
- Preserve approval, allowlist, before-state, no-snapshot, and write-verification protections.


All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Fixed
- Serialize Google SDK long-running operation handles without polling, fixing receipt creation for experiment scheduling validation.
- Include campaign drafts in exact-resource before-state and post-write verification queries, so experiment draft updates retain snapshot protection.

### Added
- Before-state capture and restore/add-back receipt recipes for readable `CampaignCriterion` ad-schedule remove operations.
- Before-state capture for supported live update operations. Saved files live under `.state/runs/<run_id>/before/`, and apply output/receipts include `before_state`.
- New preset: `optimization_pack_v1` for Search-first optimization exports with campaign pressure, keyword quality, conversion-action context, and recommendation inventory.
- New offline diagnosis command: `snapshot analyze diagnose`
  - structured findings for budget pressure, rank pressure, mixed pressure, low-volume or targeting limits, Quality Score issues, RSA issues, tracking risk, and recommendation review
  - stable JSON contract for agents
- Explicit per-RPC-method commands for Google Ads API v22 (full read + write coverage; no generic RPC bridges):
  - Command shape: `google-ads-api-tool <service-kebab> <method-kebab> --in request.json`
  - Committed RPC surface snapshots (official/client/cli) + hard-fail enforcement tests
  - Plan-first writes (dry-run plan by default) with deterministic plan fingerprints, receipts, and best-effort read-back verification
  - Deterministic spend guardrails: customer-id allowlist, global kill switch, hard caps, bounded retries/backoff, high-risk gating
- GAQL presets system (data-driven, built-in):
  - `presets list`, `presets show`, `presets validate`
- New preset: `analysis_pack_v2` (future-proof analysis pack with optional search terms, keyword metrics, device breakdown, and PMax asset context).
- New preset: `analysis_pack_max_v1` (maximal pack for deeper diagnosis: placements, landing pages, time/network, conversion-action breakdowns, RSA asset labels, budgets/settings).
  - Added geo + demographic segmentation groups (country/region/city, gender, age range) to support deeper “why it wins” analysis.
- Snapshot analysis pack export (read-only to Google Ads; writes local pack files):
  - `snapshot export` (dry-run by default; apply requires `--apply --yes`)
  - Optional groups gate: pass `--include-optional` to include `required=false` groups
  - Stable pack layout: `manifest.json`, `tables/*.jsonl`, `queries/queries.json`, `errors/errors.jsonl`
- Snapshot compare (two packs → `compare_summary.json`; descriptive only): `snapshot compare`
- Derived table: `tables/creative_anatomy.jsonl` (best-effort creative normalization)
- Docs for media buyers and agents:
  - `docs/media_buyer_quickstart.md`, `docs/winning_ads_workbook.md`, `docs/agent_recipes.md`
  - `docs/presets_reference.md`, `docs/snapshot_export_reference.md`
- Synthetic/redacted examples:
  - `docs/examples/outputs/` (presets list/show, snapshot export/compare)
  - `docs/examples/packs/minimal_pack/` (tiny manifest + rows)
- Updated the customer-ready agent skill prompt.
- Offline optimization report from exported packs:
  - `snapshot analyze optimize` (best-effort recommendations; includes candidate negative keywords when `search_terms_daily` is present)
- Helper commands for repeated live account work:
  - `helpers keywords pause-from-list`
  - `helpers keywords add-from-list`
  - `helpers campaign-negatives add-from-list`
  - `helpers campaign set-budget`
  - `helpers campaign set-max-clicks-cpc-ceiling`
  - `helpers entities lookup-by-name`
  - `helpers entities pause`
  - `helpers entities enable`
  - `helpers campaign-tree pause`
  - `helpers campaign-tree enable`
  - `helpers precheck overlap`
  - `helpers precheck policy-risk`
  - `helpers offline upload-click-conversions`
- Strict whole-campaign builders:
  - `builders search-campaign from-spec`
  - `builders competitor-search from-spec`
  - `builders dsa-feed-search from-spec`
- Example builder spec files in `docs/examples/inputs/`

### Changed
- Readable `CampaignCriterion` ad-schedule removes can now apply after before-state capture, reviewed plan, allowlist, and irreversible-risk gates. Create, upload, builder create, and unreadable remove requests still need explicit no-snapshot approval support or a true blocker reason before live apply.
- Search campaign builder specs now support `campaign.final_url_suffix` and Responsive Search Ad display paths through `path1` / `path2` or `display_path_1` / `display_path_2`.
- Search and DSA builder specs now support proximity targeting and excluded location criteria through `targeting.proximities` plus `targeting.excluded_locations` / `targeting.negative_locations`.
- `optimization_pack_v1` is now the recommended optimization workflow; `analysis_pack_v2` stays available for broader winner-analysis use.
- The documented optimization workflow is now stricter: export `optimization_pack_v1`, run `snapshot analyze diagnose`, reuse exact `recommended_doc_queries`, inspect only finding-linked tables, and treat `analysis_pack_max_v1` plus GAQL as fallback tools.
- RPC write plans/receipts are now safe-by-default: they omit raw request/response payloads unless explicitly enabled with `--include-rpc-payload --ack-sensitive-payload`.
- Reposition tool as an “analysis pack exporter” (presets-first); GAQL remains for edge cases.
- Snapshot exports now record `include_optional` in `queries/queries.json` (and in exported plan JSON when present).
- Pin supported Google Ads API version to `v22` (validated at runtime and via unit test).
- Pin the `google-ads` dependency to `29.2.0` to keep the RPC surface snapshots/tests reproducible.
- Write verification receipts now separate `verification.ok` from `verification.fully_verified`, and they record `verified_fields` plus `skipped_fields` when field-level proof is partial.
- Helper item inputs now accept CSV as well as JSON.
- Write plans and receipts now include `plain_english_summary` for faster human review.
- Builder commands now save a cleaner proof bundle in the run folder: `spec.json`, `request.json`, `builder_manifest.json`, `plan.json`, `receipt.json`, `after.json`, and `README.md`.

### Fixed
- `snapshot analyze diagnose` now weights impression-share averages by impressions instead of summing raw daily percentages.
- `snapshot analyze diagnose` now builds RSA evidence from aggregated `ad_daily_metrics` instead of zero-value metadata rows.
- `snapshot analyze diagnose` now skips empty-signal Quality Score rows and only marks high-severity QS findings when the keyword has stronger traffic or spend evidence.
- `snapshot analyze diagnose` now keeps expensive one-click Quality Score rows at medium severity unless they also have stronger traffic signal.
- Env files stored under client `.state/` folders now keep run history under `.state/runs/` instead of `.state/.state/runs/`.
- Ensure argument/usage errors in `--output json` mode emit exactly one JSON error object.
- Surface a friendly error with install guidance when the Google Ads client library is missing.
- Allow empty request JSON objects (`{}`) for RPC methods whose request message has no fields (example: `CustomerService.ListAccessibleCustomers`).
- `creative_anatomy.jsonl` join-field shape now matches the manifest join keys (dot-paths like `ad_group_ad.resource_name`).
- Ensure built-in preset JSON files ship in packaged distributions (`presets/builtin/*.json`).
- Require `--ack-spend` for budget/billing/spend-impacting RPC write methods (in addition to `--apply`/allowlist/`--yes`).
- Fix `analysis_pack_max_v1` optional groups to use GAQL fields and resources that work with the current pinned schema (campaign settings dates, hour breakdowns, geo breakdowns, age and gender breakdowns).
- Write verification now checks remove operations for absence, checks update values from `update_mask` when safe, and correctly handles important read-back table names like `campaign_criterion` and `ad_group_criterion`.
- Generic `GoogleAdsService.Mutate` writes now inspect inner `mutate_operations` for operation counts, spend-impacting detection, remove detection, and update verification extraction.

### Removed
