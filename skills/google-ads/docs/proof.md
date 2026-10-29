# Proof and verification

## Version 0.7.3 release

This release combines the keyword-create verification repair and complete direct-query handling with the v25 and receipt-safety maintenance documented below. The source, source-derived public copy and installed wheel each pass all 132 tests with network connections blocked and zero connection attempts. Public-file checks exclude private instructions, credentials, client records, caches and machine paths; relative documentation links pass. The v25/client32 command inventory is unchanged. Version and runtime hashes identify the installed copy; a previous 0.7.2 version label alone does not identify the keyword repair. Live account actions remain limited to their dated historical proof below; no new Google Ads request or mutation was used for this release.

## October 29 Mac application verified

The reviewed keyword-create repair was applied to the Mac CLI after the isolated comparison below. The exact tested runtime and tests were applied after backup. The editable installation loads this repository's source; all 132 tests pass on that path, with network connections blocked and zero connection attempts. A rebuilt wheel installed only to a temporary target also passes all 132 tests with zero connection attempts. The CLI version command returns one JSON object successfully. That application checkpoint used 0.7.2 with local changes; the combined release above is 0.7.3.

Keyword creates now compare the requested fields before full verification. Missing or unsupported comparisons remain partial and mismatches fail. Original receipts are preserved with adjacent correction notes. No Google Ads/provider requests, account changes, messages, model tests, remote installation or public publication were made for this application. The backup and full private installation receipt are retained outside the public product. The earlier isolated-preparation section below is historical proof.

## October 29 isolated keyword-create candidate

Prepared and tested offline for review; not installed or published. The original 117-test baseline passes. The candidate passes 132 tests, including 15 new regression tests; the earlier presence-only create test now requires partial verification. Remove-only absence verification stays valid.

Checks cover direct and mixed mutation requests, ordered result mapping, keyword text (including numeric text compared literally), match type, positive/negative state, ad group, requested status, omitted optional status, protobuf default false, missing fields, duplicate/missing results, unsupported fields, the existing 20-target cap, mixed create/update/remove operations and real v25 protobuf receipt serialization. Correct, mismatched, incomplete and ambiguous keyword-create receipts are saved/read back through the write engine; mutation mocks are called once with SDK retries disabled. Existing approval, snapshot, partial-failure and no-replay tests remain green.

Saved-history comparisons used three earlier keyword-create batches (6, 8 and 1 operations) with their retained post-write rows. These are offline replays, not new provider reads. The candidate compares 30, 40 and 5 requested fields; the baseline compares zero. Deliberately wrong keyword text, wrong ad groups, missing keyword fields and swapped result ordering are no longer labeled fully verified. Historical response order was reconstructed from exact request/row matches because the old receipts retain only sorted resource summaries; separate real protobuf tests exercise the native response shape and order.

No credentials were copied, and no live account changes, provider requests, new model tests or service spending were used. The existing command surface and write approvals are unchanged. Earlier live proof below belongs to its stated dates and versions.

## September 22 local completeness checks

117 local tests pass after the direct-query change. GAQL coverage includes unlimited, below-limit, exact-limit, truncated and empty results, initial read failure and failure during the one-row lookahead. Existing write-safety tests remain green. Page-size is retained as an ignored compatibility option in help and metadata. This batch changes local source and instructions only; no public release or remote installation was performed.

Google Ads proof should answer a simple question: what has actually been checked for customer access, GAQL reads, campaign settings, budgets, criteria, and bulk mutate work, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check the test count, snapshot proof, GAQL examples, and write-plan gates before trusting campaign work.

## Last verified

- Date (UTC): 2026-09-22; tool 0.7.2, Python client `google-ads==32.0.0`, API v25 including v25.1 definitions.
- Mac and OneProvider source installations: 115 tests pass. The installed wheel passes the same 115 tests. The local public layout passes 114 tests (one source-only test is intentionally absent).
- Version 0.7.2 regression: unknown, malformed, and mixed protobuf error details preserve an actual receipt file, retain known errors, count undecoded details, omit private bytes/messages, and submit once. The original provider response stays unchanged. This correction was tested offline; no live failure or mutation was induced. Token-free access/report live checks below were performed on 0.7.1, whose auth and query code is unchanged.
- New offline cases use real v25 failure protobufs to prove that partial failures return exit status 1, expose failed input locations, and omit private messages/triggers. Ambiguous timeout/unavailable/internal errors call the write method exactly once with SDK retries disabled, retain a receipt, and return `outcome_unknown`. Read retries remain tested.
- Verification cases cover no readable target, a read-back mismatch, validation-only requests, ambiguous submission despite successful read-back, and the 20-target verification cap. None may be misrepresented as fully verified completion.
- Live token-free accessible-customer reads passed on Mac and OneProvider. Both updated campaign-settings queries passed provider validation on Mac and returned a live row on both installations. The checks displayed success booleans only, not account payloads or credentials.
- Previous 0.7.0 migration proof: all 38 unique bundled queries and one campaign-update payload passed validation-only checks. In 0.7.1 only the two campaign-settings queries changed; those were revalidated above.
- The 169-method inventory and request-resolution checks prove command mapping, not live behavior of every API method. Create, conversion upload, billing, reservation, authorization, and asynchronous workflows were not live-executed by this maintenance task.
- No campaign, budget, targeting, tracking, or conversion mutation was applied. Failure tests were synthetic.
- Mac and OneProvider now run 0.7.2. A pre-maintenance source archive was retained on OneProvider for rollback; credentials were not modified. The local public mirror is staged only; no Git commit, push, or public publication was performed.
- Historical examples below retain their original versions and capture dates.

## Smoke checks

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

## What can go wrong

- **Invalid OAuth setup / Cloud project access** → verify `auth check` returns `ok=false`, and the error message does not echo secret env values.
- **No accessible customers** → verify `auth check` returns `ok=true` but `customer_count=0`.
- **Large queries** → verify `gaql --limit N` truncates results deterministically and sets `meta.limited=true`.
- **Export truncation** → verify `manifest.json` records `truncated=true` and includes a warning when `--max-rows` is hit.
- **Missing diagnose families** → verify `tables_missing` explains which finding families were skipped, then re-export with `optimization_pack_v1` or `--include-optional` as needed.
- **Write apply needs a safety gate** → inspect `reasons`; create/upload/builder create and unreadable remove requests need explicit `--ack-no-snapshot` approval before live apply.
- **Write receipt says `ok=true` but `fully_verified=false`** → inspect `verification.skipped_fields`; the write did not show a mismatch, but the tool could not prove every updated field from read-back.
- **Before-state review** → inspect `before_state.saved`; supported updates and readable ad-schedule removes save the prior resource fields under `.state/runs/<run_id>/before/`.
- **Ad-schedule add-back review** → inspect `restore_recipes` on readable ad-schedule remove receipts.
- **You need a faster human read of a plan or receipt** → inspect `plain_english_summary` first, then move into `request_summary`, `risk`, and `verification`.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
