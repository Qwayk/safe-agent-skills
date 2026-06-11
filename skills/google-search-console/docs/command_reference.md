# Command reference

Use this page when you need the exact Google Search Console command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags (selected)

- `--env-file .env` (default)
- `--output json|text` (default: `json`)
- `--apply` (required for write methods)
- `--yes` (extra confirmation for destructive/batch writes)
- `--ack-irreversible` (extra acknowledgement for deletes)
- `--plan-out plan.json` (write a dry-run plan)
- `--plan-in plan.json` (apply from a reviewed plan; required for deletes; produce it with a dry-run using `--plan-out plan.json`)
- `--receipt-out receipt.json` (write an apply receipt)
- Recovery info appears in `plan.recovery` and `receipt.recovery` for write methods.
- Write plans and receipts also carry a live pre-state snapshot in `before_state`.
- When output is stored in run artifacts, `before_state_path` points at `before_state.json`.
- `--run-id 2026-03-05T120000Z_example` (attach a deterministic run id)

## Onboarding

- `gsc-api-tool onboarding [--no-write-env]`

## Auth

- `gsc-api-tool --output json --version`
- `gsc-api-tool auth check`
- `gsc-api-tool auth login`

## Operations (offline)

- `gsc-api-tool operations list`
- `gsc-api-tool operations validate`

## Google Search Console methods (100% of pinned discovery snapshot)

Body rules:
- Methods that require a request body accept **exactly one of** `--body-json` or `--body-file`.

Read-like POSTs (no `--apply` needed):
- `gsc-api-tool searchanalytics query --site-url https://example.com/ --body-json '{"startDate":"2026-03-01","endDate":"2026-03-05","dimensions":["query"]}'`
- `gsc-api-tool url-inspection index inspect --body-json '{"inspectionUrl":"https://example.com/","siteUrl":"sc-domain:example.com"}'`
- `gsc-api-tool url-testing-tools mobile-friendly-test run --body-json '{"url":"https://example.com/"}'`

Sites:
- `gsc-api-tool sites list`
- `gsc-api-tool sites get --site-url https://example.com/`
- `gsc-api-tool sites add --site-url https://example.com/` (write; dry-run plan by default)
- `gsc-api-tool --apply sites add --site-url https://example.com/` (recovery: `rollback_by_inverse_action` via `webmasters.sites.delete`)
- `gsc-api-tool sites delete --site-url https://example.com/` (delete; extra gates)
- `gsc-api-tool --plan-out plan.json sites delete --site-url https://example.com/` (dry-run; writes plan file used for delete apply)
- `gsc-api-tool --apply --yes --ack-irreversible --plan-in plan.json sites delete --site-url https://example.com/` (recovery: `irreversible_and_clearly_labeled`)
- `gsc-api-tool --run-id 2026-03-05T130000Z_add --plan-out .state/runs/2026-03-05T130000Z_add/plan.json sites add --site-url https://example.com/` (plan captures `before_state`)

Sitemaps:
- `gsc-api-tool sitemaps list --site-url https://example.com/`
- `gsc-api-tool sitemaps get --site-url https://example.com/ --feedpath https://example.com/sitemap.xml`
- `gsc-api-tool sitemaps submit --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (write; dry-run plan by default)
- `gsc-api-tool --apply sitemaps submit --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (recovery: `rollback_by_inverse_action` via `webmasters.sitemaps.delete`)
- `gsc-api-tool sitemaps delete --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (delete; extra gates)
- `gsc-api-tool --plan-out plan.json sitemaps delete --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (dry-run; writes plan file used for delete apply)
- `gsc-api-tool --apply --yes --ack-irreversible --plan-in plan.json sitemaps delete --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (recovery: `irreversible_and_clearly_labeled`)
- `gsc-api-tool --apply --yes --ack-irreversible --plan-in .state/runs/2026-03-05T131500Z_plan_del/plan.json --run-id 2026-03-05T131600Z_apply_del sitemaps delete --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` (checks `before_state` in output/receipt)

## Runs (local history)

Write-capable commands save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.
These live next to your `--env-file`.

- `gsc-api-tool runs list [--limit 20]`
- `gsc-api-tool runs show --run-id 2026-03-05T120000Z_example`
