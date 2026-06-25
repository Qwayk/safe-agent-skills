# Proof and verification

Most users will never need to run these commands themselves. This proof page answers what has actually been checked, what was only tested locally, and what still needs a real Contentsquare read before anyone claims live account behavior.

The short version: local tests, docs checks, safety gates, and redacted examples passed; live Contentsquare account behavior has not been verified yet.

A good evidence request is: "Show me what has already been verified for Contentsquare, what is still live-unverified, and the first safe read needed for real account proof." If you only check one thing, check whether the reported proof came from a local test, a redacted example, or a real Contentsquare account read.

## What this page proves

- the CLI installs
- the local test suite passes
- the docs contract checks pass
- committed examples are redacted safe-shape examples
- OAuth request bodies, query names, plan gates, receipts, and redaction are covered by tests

This page does not prove that a real Contentsquare project, metric, export job, enrichment integration, or Speed Analysis report was read successfully.

## Last verified

- Date (UTC): `2026-06-25`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider source: official Contentsquare server-side REST docs
- Environment: local source build; no live Contentsquare account verification yet

## Smoke checks

Run inside the tool folder.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

Check the command:

```bash
contentsquare-safe-cli --output json --version
```

Check local OAuth setup:

```bash
contentsquare-safe-cli --output json auth check
```

`auth check` proves whether the local OAuth fields can obtain a token. It does not prove that every live Contentsquare API family is entitled for the account.

## Latest local validation

Run on 2026-06-25:

- Tool install: passed with `.venv/bin/python -m pip install -e .`
- Unit tests: passed, 46 tests
- Repo new-tool audit: passed
- Control-room alignment audit: passed
- Diff whitespace check: passed with `git diff --check`
- OAuth request-shape tests: passed for `auth check`, `auth me`, Data Export, Metrics, Enrichment, Speed Analysis Lab, explicit scope override, account-level `project_id`, and refusal of unsafe combined Enrichment scopes

## What local tests prove

- The CLI imports cleanly.
- The command catalog has 82 documented server-side rows.
- Write commands dry-run before auth and require reviewed apply for live changes.
- Read commands send official Contentsquare query parameter names such as `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `period`, `ids`, `state`, `order`, `format`, `frequency`, `scope`, `from`, and `to`.
- Data Export file downloads use the documented nested `files[].url` values from the run lookup and refuse to guess when a run has multiple files; tests cover choosing by `--file-index` and by `--part-id`.
- OAuth token requests send the official API-family scopes: `data-export`, `metrics`, `enrichment`, and `speed-analysis`.
- Account-level OAuth token requests can include the documented `project_id` from `CONTENTSQUARE_PROJECT_ID` or `--oauth-project-id`.
- `auth me` sends the documented `client_id` / `client_secret` body to `/v1/oauth/me`.
- Enrichment scope overrides refuse combined scopes because the official docs say Enrichment cannot be combined with other scopes.
- Auth errors do not print configured secret values.
- Public docs reject starter copy and raw-request shortcuts.

## What still needs live credentials

Live Contentsquare OAuth credentials are required to prove account-specific scopes, endpoint routing, and provider responses. Missing live credentials are not by itself a source-build blocker; live behavior must stay marked unverified until a safe Contentsquare project is available.

## What can go wrong

- **OAuth credentials are missing.** `auth check` returns a credential error and no write runs.
- **The project is wrong.** Account-level credentials may need `CONTENTSQUARE_PROJECT_ID` or `--oauth-project-id`.
- **The account lacks an entitlement.** Contentsquare may reject a Metrics, Enrichment, Data Export, or Speed Analysis request even when OAuth works.
- **A date range is too wide.** Metrics date ranges cannot exceed the documented limit.
- **An export file expired.** Data Export generated files expire after the documented period.
- **Verification is limited.** Write receipts can record the provider response, but some actions have no safe universal before/after snapshot in the official docs.

## Redacted examples

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/data_export_list_jobs.json`
- `docs/examples/outputs/metrics_site_bounce_rate.json`
- `docs/examples/outputs/data_export_download_run_file.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
