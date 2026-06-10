# Proof pack (publish-ready evidence)

Purpose:
- Make this tool “proof-first” for future posts/pages (E‑E‑A‑T).
- Capture the minimal evidence a customer can trust: what ran, what came back, what can go wrong, and how we verify.

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Use obvious redactions/placeholder values in examples.
- Keep this file short and factual.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: Codex (local tests only; no live Dynadot account verification)
- Tool version: 0.5.0
- Provider API version (if applicable): Dynadot API3 (command-based)
- Environment: expected prod base URL is https://api.dynadot.com/api3.json (not executed here)

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `dynadot-api-tool --output json --version`

3) Auth/config check (read-only):
- `dynadot-api-tool --output json auth check`

4) One representative inventory export (read-only):
- `dynadot-api-tool --output json domains list --page 1 --out domains.list.json`

5) One representative read query:
- `dynadot-api-tool --output json domains push-requests list`

5b) API3 full coverage discovery (local-only help text):
- `dynadot-api-tool api3 --help`

6) Domain push (preview only):
- `dynadot-api-tool --output json --plan-out plan.json domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>"`

7) Accept a push request (apply-gated, receiver side):
- `dynadot-api-tool --output json --apply --yes --plan-in plan.json domains push-requests accept --domains-file "<FILE>"`
  - Expected result: approved apply records explicit no-snapshot approval and recovery limits; missing approval refuses before Dynadot write HTTP.

8) Name server audit (read-only):
- `dynadot-api-tool --output json domains name-servers export --domains-export-in domains.list.json --out name_servers.current.json`
- `dynadot-api-tool --output json domains name-servers diff --current-in name_servers.current.json --desired-ns "ns1.example.net" --desired-ns "ns2.example.net" --out name_servers.diff.json`

9) Name server set (preview only):
- `dynadot-api-tool --output json --plan-out plan.json domains name-servers set --diff-in name_servers.diff.json`

10) Transfer run (preview only):
- `dynadot-api-tool --output json --plan-out plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"`

Notes for large runs:
- You can safely resume some write actions using `--resume-from-receipt`.
- If verification hits API limits, slow it down with `--sleep-between-verifications-s` (name servers set).

## Local validation on 2026-06-04

- `.venv/bin/python -m unittest -q tests.test_write_recovery_contract tests.test_api3_commands tests.test_jobs tests.test_domains_safety tests.test_bulk_pacing tests.test_name_servers tests.test_transfer_run tests.test_run_artifacts`
  - `50 tests, OK`
- `.venv/bin/python -m unittest -q`
  - `124 tests, OK`
- `.venv/bin/python -m unittest -q tests.test_docs_formatting`
  - `1 test, OK`
- `.venv/bin/python -m dynadot_api_tool --output json --version`
  - passed
- Committed JSON examples under `docs/examples/`
  - parsed successfully

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/account_info.json`
- `docs/examples/outputs/get_account_balance.json`
- `docs/examples/outputs/list_coupons.json`
- `docs/examples/outputs/tld_price.json`
- `docs/examples/outputs/search.json`
- `docs/examples/outputs/name_servers_export.summary.json`
- `docs/examples/outputs/name_servers_diff.summary.json`
- `docs/examples/outputs/name_servers_set.plan.json`
- `docs/examples/outputs/name_servers_set.receipt.json`
- `docs/examples/outputs/transfer_run.plan.json`
- `docs/examples/outputs/transfer_run.receipt.json`
- `docs/examples/outputs/transfer_domain_list.json`
- `docs/examples/outputs/get_transfer_status.json`
- `docs/examples/outputs/get_transfer_auth_code.json`
- `docs/examples/outputs/order_list.json`
- `docs/examples/outputs/get_order_status.json`
- `docs/examples/outputs/contact_list.json`
- `docs/examples/outputs/get_contact.json`
- `docs/examples/outputs/get_dns.json`
- `docs/examples/outputs/get_listings.json`
- `docs/examples/outputs/get_listing_item.json`
- `docs/examples/outputs/get_open_auctions.json`
- `docs/examples/outputs/get_closed_auctions.json`
- `docs/examples/outputs/get_auction_details.json`
- `docs/examples/outputs/get_auction_bids.json`
- `docs/examples/outputs/get_closed_backorder_auctions.json`
- `docs/examples/outputs/get_backorder_auction_details.json`
- `docs/examples/outputs/get_expired_closeout_domains.json`
- `docs/examples/outputs/backorder_request_list.json`
- `docs/examples/outputs/get_cn_audit_status.json`
- `docs/examples/outputs/api3_register.plan.json`
- `docs/examples/outputs/api3_set_privacy.plan.json`
- `docs/examples/outputs/api3_place_auction_bid.plan.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong (and how we verify)

- **Invalid API key / wrong scopes** → verify with `auth check` returning `ok=false` and a clear error type; confirm no writes occurred.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify writes require `--apply` (and `--yes` + reviewed `--plan-in`), then require explicit no-snapshot approval before Dynadot HTTP because before-state support is missing:
  - `before_state.required = true`
  - `before_state.supported = false`
  - `before_state.status = no_snapshot_available`
- Verify the plan includes the explicit no-recovery contract:
  - `recovery.end_state = irreversible_and_clearly_labeled`
  - `recovery.backups: []`
  - `recovery.snapshots: []`
  - `recovery.rollback_plan: null`
- Future verification notes may still be present as `post_apply_verification_plan`, but they do not unlock apply.
- **Write receipt** → verify approved apply records no-snapshot approval and recovery limits; missing approval creates only refusal output.
- **Snapshot wording drift** → verify docs never describe read-back snapshot verification as a restoreable backup.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
