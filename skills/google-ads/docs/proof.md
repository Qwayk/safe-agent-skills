# Proof pack (publish-ready evidence)

Purpose:
- Capture the minimal evidence a customer can trust: what ran, what came back, what can go wrong, and how we verify.

Rules:
- Never include secrets.
- Keep this file short and factual.

Reassurance:
- You don’t need to run these commands yourself; they exist for auditing and proof.

## Last verified

- Date (UTC): 2026-06-06
- Verified by: agent (unit tests, helper and builder command tests, before-state tests, readable ad-schedule remove tests, and one earlier read-only real export/diagnose proof)
- Tool version: 0.6.0
- Provider API version: v22 (RPC surface snapshots + enforcement tests; no live API calls)
- Validation result: `.venv/bin/python -m unittest -q` passed after readable ad-schedule remove support was added; 97 tests passed.

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `google-ads-api-tool --output json --version`

3) Onboarding help (creates `.env` from `.env.example`):
- `google-ads-api-tool --output json onboarding`

4) Auth/config check (read-only; requires a configured `.env`):
- `google-ads-api-tool --output json auth check`

5) Presets list (no `.env` required):
- `google-ads-api-tool --output json presets list`

6) Snapshot export (dry-run; no API calls, no pack folder written):
- `google-ads-api-tool --output json snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack`

7) Snapshot export (apply; requires real credentials; read-only to Google Ads, writes local pack files):
- `google-ads-api-tool --output json snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes --overwrite`
- Snapshot output is saved for local evidence only and is not a restore/rollback mechanism.
- Include optional groups (deeper analysis; may increase time/quota): add `--include-optional`

8) One representative read query (GAQL; optional/edge cases):
- `google-ads-api-tool --output json gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT customer.id FROM customer LIMIT 1" --limit 1`

9) One representative write plan (RPC; dry-run by default; no mutation):
- `google-ads-api-tool --output json campaign-service mutate-campaigns --in ./mutate_campaigns_request.json`

10) One representative write apply (RPC; requires allowlist + real credentials):
- `google-ads-api-tool --output json campaign-service mutate-campaigns --in ./mutate_campaigns_request.json --apply --yes --plan-in ./plan.json`
- For budget/billing/spend-impacting write methods, also pass `--ack-spend` (in addition to `--yes`).

10b) One representative helper write plan (same safety model, less JSON by hand):
- `google-ads-api-tool --output json helpers campaign set-budget --customer-id YOUR_CUSTOMER_ID --budget-id YOUR_BUDGET_ID --amount 70`

10bb) One representative helper name lookup (read-only):
- `google-ads-api-tool --output json helpers entities lookup-by-name --customer-id YOUR_CUSTOMER_ID --resource-type campaign --name "Main Search"`

10bc) One representative helper precheck (read-only):
- `google-ads-api-tool --output json helpers precheck overlap --customer-id YOUR_CUSTOMER_ID`

10c) One representative builder write plan (same safety model, strict whole-campaign spec):
- `google-ads-api-tool --output json builders search-campaign from-spec --spec ./docs/examples/inputs/builder_search_campaign_spec.json`

11) Offline optimization diagnosis from an exported pack (no API calls):
- `google-ads-api-tool --output json snapshot analyze diagnose --pack-dir ./out/google-ads-pack`

12) Legacy best-effort optimization report from an exported pack:
- `google-ads-api-tool --output json snapshot analyze optimize --pack-dir ./out/google-ads-pack`

## Offline proof artifacts (no live API)

- Unit tests: `python3 -m unittest -q`
- Redacted outputs: see the files listed below in “Example outputs (synthetic / redacted)”.

## Example outputs (synthetic / redacted)

These files are committed:
- `docs/examples/version.json`
- `docs/examples/onboarding.json`
- `docs/examples/gaql_sample.json`
- `docs/examples/inputs/builder_search_campaign_spec.json`
- `docs/examples/inputs/builder_competitor_search_spec.json`
- `docs/examples/inputs/builder_dsa_feed_search_spec.json`
- `docs/examples/outputs/rpc_write_plan_dry_run.json`
- `docs/examples/outputs/rpc_write_apply_receipt.json`
- `docs/examples/outputs/rpc_write_refusal_allowlist.json`
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/presets_list.json`
- `docs/examples/outputs/presets_show_optimization_pack_v1.json`
- `docs/examples/outputs/presets_show_analysis_pack_v1.json`
- `docs/examples/outputs/presets_show_analysis_pack_v2.json`
- `docs/examples/outputs/presets_show_analysis_pack_max_v1.json`
- `docs/examples/outputs/snapshot_export_dry_run.json`
- `docs/examples/outputs/snapshot_export_apply_summary.json`
- `docs/examples/outputs/snapshot_compare_apply_summary.json`
- `docs/examples/outputs/snapshot_analyze_optimize.json`
- `docs/examples/packs/minimal_pack/manifest.json`

## What can go wrong (and how we verify)

- **Invalid developer token / OAuth setup** → verify `auth check` returns `ok=false`, and the error message does not echo secret env values.
- **No accessible customers** → verify `auth check` returns `ok=true` but `customer_count=0`.
- **Large queries** → verify `gaql --limit N` truncates results deterministically and sets `meta.limited=true`.
- **Export truncation** → verify `manifest.json` records `truncated=true` and includes a warning when `--max-rows` is hit.
- **Missing diagnose families** → verify `tables_missing` explains which finding families were skipped, then re-export with `optimization_pack_v1` or `--include-optional` as needed.
- **Write apply needs a safety gate** → inspect `reasons`; create/upload/builder create and unreadable remove requests need explicit no-snapshot approval support or a true blocker reason before live apply.
- **Write receipt says `ok=true` but `fully_verified=false`** → inspect `verification.skipped_fields`; the write did not show a mismatch, but the tool could not prove every updated field from read-back.
- **Before-state review** → inspect `before_state.saved`; supported updates and readable ad-schedule removes save the prior resource fields under `.state/runs/<run_id>/before/`.
- **Ad-schedule add-back review** → inspect `restore_recipes` on readable ad-schedule remove receipts.
- **You need a faster human read of a plan or receipt** → inspect `plain_english_summary` first, then move into `request_summary`, `risk`, and `verification`.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
