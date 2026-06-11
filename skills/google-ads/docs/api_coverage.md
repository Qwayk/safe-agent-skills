# API coverage (Google Ads API → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give reviewers a single main reference for what exists.

Rules:
- Keep this table honest. If something is missing, list it as missing.

## Summary

- Provider: Google Ads API
- API host: googleads.googleapis.com (via Google Ads API client library)
- Supported API version: v22
- Auth method: OAuth2 (refresh token) + developer token
- Last audited (UTC): 2026-06-06
- Before-state policy: supported update operations and readable `CampaignCriterion` ad-schedule removes save before-state under `.state/runs/<run_id>/before/`; create, upload, unreadable removes, and other unsupported live write shapes need explicit no-snapshot approval support or a true blocker reason before live apply.

## “100% coverage” definition (enforced)

Definition:
- “100% coverage” means: every official Google Ads API RPC service method for the supported version (v22) is mapped 1:1 to an explicit `google-ads-api-tool <service-kebab> <method-kebab>` command.
- No generic “call any RPC” bridges are allowed.

Reproducible surface snapshots (committed):
- Official RPC surface: `docs/official_rpc_surface_v22_2026-03-01.txt`
- Client (installed `google-ads`) RPC surface: `docs/client_rpc_surface_v22_2026-03-01.txt`
- CLI RPC surface: `docs/cli_rpc_surface_v22_2026-03-01.txt`

Enforcement:
- Unit tests hard-fail unless the three surfaces match exactly: `tests/test_rpc_surface_coverage.py`.

## Coverage

| Google Ads surface | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| Google Ads RPC surface (all services/methods; v22) | Full read + write coverage (explicit per-RPC method commands) | `google-ads-api-tool <service-kebab> <method-kebab> --in request.json` | Writes are plan-first by default; supported update apply and readable ad-schedule remove apply require before-state + `--apply` + allowlist + risk gates; other create/remove/upload shapes need explicit no-snapshot approval support or a true blocker reason | `tests/test_rpc_surface_coverage.py`, `tests/test_rpc_before_state.py`, `docs/examples/outputs/` | CLI commands are generated from the pinned `google-ads` client descriptors; the official surface snapshot is curated from the official v22 RPC reference, and unit tests enforce that official == client == CLI. |
| CustomerService.ListAccessibleCustomers | Auth/connectivity smoke test | `google-ads-api-tool auth check` | Read-only | `tests/test_auth_check_no_secrets.py` | Does not print secret values. |
| CustomerService.ListAccessibleCustomers | List accessible customer ids | `google-ads-api-tool customers list-accessible` | Read-only | (see proof examples) | IDs parsed from resource names. |
| GoogleAdsService.Search | Run arbitrary GAQL queries | `google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query \"YOUR_GAQL_QUERY\"` | Read-only | `tests/test_gaql_limit.py`, `docs/examples/gaql_sample.json` | `--limit` enforced client-side. |
| GoogleAdsService.Search | Preset-driven snapshot export (optimization pack) | `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack` | Dry-run by default; apply requires `--apply --yes`; read-only to Google Ads | `tests/test_presets_commands.py`, `tests/test_optimization_pack_v1_gaql_fields.py`, `tests/test_snapshot_export_*.py` | Exports diagnosis-ready campaign pressure, keyword quality, conversion-action, and recommendation tables. |
| GoogleAdsService.Search | Preset-driven snapshot export (analysis pack) | `google-ads-api-tool snapshot export --preset analysis_pack_v2 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack` | Dry-run by default; apply requires `--apply --yes`; read-only to Google Ads | `tests/test_snapshot_export_*.py` | Writes local pack files: manifest + JSONL tables + queries + errors. By default exports `required=true` groups; pass `--include-optional` to include optional groups. |
| Local pack analysis | Offline optimization diagnosis | `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack` | Read-only | `tests/test_snapshot_analyze_diagnose.py` | Returns structured findings, actions, and doc-query hints from an exported pack. |
| GoogleAdsFieldService.SearchGoogleAdsFields | Search field metadata | `google-ads-api-tool fields search --query \"YOUR_FIELDS_QUERY\"` / `--contains YOUR_SUBSTRING` | Read-only | (see proof examples) | Convenience `--contains` builds a deterministic query. |
| Helper layer (strict wrappers over explicit RPC writes) | Repeated live account changes without hand-writing full request envelopes | `google-ads-api-tool helpers ...` | Same write gates as RPC writes; update helpers can apply with before-state; create/upload helpers still need explicit no-snapshot approval support | `tests/test_helpers_commands.py`, `tests/test_helpers_csv_input.py`, `tests/test_helpers_lookup_by_name.py`, `tests/test_helpers_campaign_tree.py`, `tests/test_rpc_before_state.py` | Current helper slice covers keyword pauses, keyword adds, campaign negatives, budget changes, Maximize Clicks CPC ceilings, entity lookup by name, full campaign-tree enable/pause, CSV item input, overlap prechecks, policy-risk prechecks, and click conversion uploads. |
| Builder layer (strict wrappers over `GoogleAdsService.Mutate`) | Whole campaign creation from reviewed spec files | `google-ads-api-tool builders ... from-spec --spec ./spec.json` | Plan-first; not the current live-change path for create-heavy requests until snapshot support or explicit no-snapshot approval support exists | `tests/test_builders_commands.py`, `tests/test_rpc_write_safety_gates.py`, `tests/test_rpc_write_verification.py`, `tests/test_rpc_before_state.py` | Current builder slice covers standard Search campaigns, competitor Search campaigns, and page-feed-only DSA Search campaigns. |

## Notes / limitations (explicit)

- Unit tests are offline-only: they validate command surfaces and safety contracts without calling Google Ads APIs.
- Live API calls (reads and writes) require real credentials and a configured allowlist; orchestrator proof runs do not mutate real accounts.
- RPC write plans/receipts are safe-by-default (no raw request/response payloads) unless explicitly enabled with `--include-rpc-payload --ack-sensitive-payload`.
- Before-state currently covers update operations with readable resource names and update masks plus readable `CampaignCriterion` ad-schedule removes. Create, upload, unreadable removes, and non-operation write requests still need explicit no-snapshot approval support or a true blocker reason before live apply.
