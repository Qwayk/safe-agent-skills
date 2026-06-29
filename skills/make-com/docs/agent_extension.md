# Agent extension guide

Use this page when an AI coding assistant is adding or changing commands in the source tool.

The goal is simple: keep Make API coverage tied to the official inventory, keep changes easy to review, and keep writes safe by default.

## Repo map

- `src/<package>/cli.py`: CLI wiring
- `src/<package>/commands/api.py`: inventory-backed Make API command runner
- `src/<package>/config.py`: `.env` parsing and validation
- `src/<package>/http.py`: HTTP wrapper (never log secrets)
- `src/<package>/output.py`: stdout contract (one JSON object)
- `src/<package>/audit_log.py`: JSONL audit log (redaction)
- `scripts/refresh_official_inventory.py`: official Make API inventory refresh
- `docs/official_inventory.json`: pinned source of documented Make operations
- `tests/`: unit tests (prefer mocks, no real network)

## Add or refresh a Make API operation

1. Refresh `docs/official_inventory.json` from the official Make Developer Hub pages.
2. Confirm the operation appears under `make-com-safe api list`.
3. Use `api schema <family> <operation>` to inspect required path, query, body, and scope data.
4. Add or update tests only when parser behavior, safety behavior, output shape, or inventory assumptions changed.
5. Update `docs/api_coverage.md`, `docs/command_reference.md`, and `docs/proof.md` when the inventory or safety behavior changes.

Do not add a raw URL command, free-form HTTP command, Make CLI wrapper, MCP wrapper, or SDK pass-through.

## Write safety

All Make writes use the inventory-backed runner. The expected flow is:

1. dry-run plan,
2. human review,
3. apply from `--plan-in --apply --yes`,
4. `--ack-no-snapshot` when the inventory marks no safe snapshot,
5. `--ack-irreversible` for destructive operations,
6. receipt output and run history when enabled.

Add tests for:
- plan redaction for blueprint, token, connection, webhook, and secret-like fields
- command redaction for raw `--body-json` values and `--body-file` paths across stdout, plans, run summaries, run indexes, audit logs, and receipts
- command, target, and receipt URL redaction for secret-looking `--path-param` and `--query` values, with exact apply validation through target fingerprints
- refusal when the current credential fingerprint differs from the reviewed plan
- refusal without `--plan-in`
- refusal without `--yes`
- refusal without `--ack-no-snapshot` for no-snapshot writes
- receipt output shape when mocked live apply is added

## Run history

Write-capable Make API commands auto-save run artifacts under:
- `.state/runs/<run_id>/`

When changing commands:
- Keep `write_capable=True` for all non-read Make operations.
- Keep outputs deterministic and ensure plans/receipts never include secrets.

## Review prompts (recommended, optional)

Ship prompts to help users review plans and receipts safely:
- `docs/plan_review_prompt.md`
- `docs/receipt_review_prompt.md`
