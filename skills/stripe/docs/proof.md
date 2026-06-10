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
- Provider API version: pinned OpenAPI snapshot `2026-02-25.clover` (see `docs/references.md`)
- Environment: offline-only (no live Stripe API calls) / base URL: `https://api.stripe.com`

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `stripe-api-tool --output json --version`

3) Pinned inventory validate (no `.env` required):
- `stripe-api-tool --output json inventory validate`

4) Unit tests:
- `python3 -m unittest -q`

5) Example plan output (synthetic; no live calls):
- `stripe-api-tool --output json --env-file docs/examples/stripe.env.example api post-payment-intents --data amount=100 --data currency=usd`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (safe API write refusal example; no live API receipt exists today)

## What can go wrong (and how we verify)

- **No saved snapshot / no automatic rollback** -> every API write plan must include `before_state.supported=false` and a `rollback` block with `supported=false`; live API write apply requires explicit no-snapshot approval before Stripe HTTP when no saved snapshot is available.

- **Missing `STRIPE_API_KEY`** → verify `stripe-api-tool --output json auth check` fails fast with a clear error, and no API calls are made.
- **Invalid API key** (looks valid but doesn't work) → verify with a read-only live call like `stripe-api-tool --output json api --live get-account`.
- **Rate limiting / transient network errors** → verify the HTTP layer retries a small, capped number of times (and stops after the retry budget); use `--verbose` to see retry timing.
- **Write safety drift** → verify write-like operations do not execute without `--apply`, high-risk operations require `--yes --plan-in` first, and fully gated live writes still require explicit no-snapshot approval before Stripe HTTP when no saved snapshot or provider backup exists.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
