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
- Verified by: agent
- Tool version: 0.1.0
- Provider API version: 2026-01 (pinned)
- Verification mode: offline unit tests only (no live Shopify calls)
- Endpoint format (for real runs): `https://{SHOPIFY_SHOP_DOMAIN}/admin/api/{SHOPIFY_ADMIN_API_VERSION}/graphql.json`

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `shopify-admin-api-tool --output json --version`

3) Auth/config check (read-only):
- `shopify-admin-api-tool --output json auth check`

4) One representative read query:
- `shopify-admin-api-tool --output json query shop`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved supported writes emit receipts when live access and required approvals are available)

## What can go wrong (and how we verify)

- **Invalid API key / wrong scopes** → verify with `auth check` returning `ok=true` but showing `graphql.http_status` >= 400 and/or `graphql.has_errors=true` (and typically `graphql.shop_id_present=false`). `ok=false` is reserved for tool/runtime errors like missing config or non-JSON responses.
- **Rate limiting** → verify the CLI surfaces `graphql.http_status=429`. The tool does not auto-retry or back off (it sets `retries=0`), so your caller must implement backoff/jitter if needed.
- **Pagination surprises** → verify pagination is user-controlled via the GraphQL operation and return shape. The tool does not auto-paginate or add “next page” hints; for connections you must supply pagination vars (for example `first`/`after`) and request the relevant `pageInfo`/`edges` fields in `--return-shape-file`.
- **Write safety drift** (mutations) → verify mutation dry-runs create plans, and `--apply` requires explicit no-snapshot approval before Shopify HTTP when no operation-specific saved snapshot is available. Higher-risk mutations still enforce the required flags first (`--yes`, `--plan-in`, and `--ack-irreversible` when applicable).

- **Write recovery** (rollbacks/restores) -> this tool does not create backups or restore points and does not auto-rollback. Mutation apply requires explicit no-snapshot approval when no generic before-state path is safe enough for the whole Shopify Admin surface, and the receipt must record that limit.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
