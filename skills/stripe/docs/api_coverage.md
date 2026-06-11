# API coverage (endpoints → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give the Manager a single source of truth for review/approval.
- Help customers quickly see what the tool can and cannot do.

Rules:
- Keep this table honest. If something is missing, list it as missing.
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
