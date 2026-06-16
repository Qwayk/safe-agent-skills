# API coverage

Stripe coverage shows exactly what the shipped commands can do with customers, subscriptions, invoices, payments, refunds, payouts, and connected accounts. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether the shipped commands can inspect customers, subscriptions, and invoices, then show which Stripe money actions need reviewed apply steps."

## Coverage notes

- Give the Manager a single main reference for review/approval.
- Help customers quickly see what the tool can and cannot do.
- If behavior differs from the provider docs, note it and link `docs/references.md`.

## Summary

- Provider: Stripe
- API base URL: `https://api.stripe.com`
- Auth method: API key (Bearer)
- Pinned OpenAPI snapshot: `docs/official_openapi_2026-02-25.clover_2026-03-05.json`
- Operation inventory: `docs/official_operations_2026-02-25.clover_2026-03-05.txt` (587 operations)
- Command inventory: `docs/official_commands_2026-02-25.clover_2026-03-05.txt` (587 commands)
- Last audited (UTC): 2026-06-04
- API write safety: preview first. When no saved snapshot or provider backup is available, live API write apply can still run after review and explicit `--ack-no-snapshot` approval.

## Endpoint coverage

Columns:
- Endpoint
- Capability
- CLI command(s)
- Safety gates (dry-run/read-live/write-refusal)
- Tests/examples
- Notes

Coverage definition (“100%”):
- Every operation in the pinned OpenAPI snapshot has exactly one explicit CLI command under `stripe-api-tool api ...`.
- Enforced offline by `inventory validate` and by unit tests (no guessing).

## Known gaps (explicit)

None known for the pinned snapshot (coverage is enforced mechanically).
