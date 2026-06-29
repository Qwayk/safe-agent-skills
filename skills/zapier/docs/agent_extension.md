# Agent extension guide

Use this page when an AI coding assistant is adding or changing commands in the source tool.

The goal is simple: keep changes easy to review, safe by default, and covered by tests.

## Repo map

- `src/<package>/cli.py`: CLI wiring
- `src/<package>/commands/`: command handlers
- `src/<package>/config.py`: `.env` parsing and validation
- `src/<package>/http.py`: HTTP wrapper (never log secrets)
- `src/<package>/output.py`: stdout contract (one JSON object)
- `src/<package>/audit_log.py`: JSONL audit log (redaction)
- `tests/`: unit tests (prefer mocks, no real network)

## Add a read command

1. Create `src/<package>/commands/<name>.py`.
2. Implement `cmd_<name>(args, ctx) -> int`.
3. Register it in `cli.py`.
4. Emit exactly one JSON object in JSON mode.
5. Add a unit test for the output shape.

## Add a write command

Safety checks:
- Dry-run by default (no writes without `--apply`).
- Batch/destructive writes require `--apply --yes`.
- Verify after write (read-back or idempotence).
- Refuse when unsure.

Recommended workflow:
- preview
- review
- apply
- verify
- receipt

Recommended flags when the command supports them:
- `--plan-out <path>` (save plan for review)
- `--plan-in <path>` (apply from a reviewed plan)
- `--receipt-out <path>` (save receipt for audit)

Add tests for:
- refusal without `--apply`
- refusal without `--yes` for risky writes
- verification behavior (mocked)

## Run history (recommended)

This tool auto-saves proof artifacts for write-capable commands under:
- `.state/runs/<run_id>/`

When adding new commands:
- Mark the CLI parser with `write_capable=True` so run history is enabled by default.
- Keep outputs deterministic and ensure plans/receipts never include secrets.

## Review prompts (recommended, optional)

Ship prompts to help users review plans and receipts safely:
- `docs/plan_review_prompt.md`
- `docs/receipt_review_prompt.md`
