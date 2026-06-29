# Agent extension guide

## Repo map

- `src/openai_api_tool/cli.py`: CLI wiring
- `src/openai_api_tool/commands/`: command handlers
- `src/openai_api_tool/config.py`: `.env` parsing and validation
- `src/openai_api_tool/http.py`: HTTP wrapper (never log secrets)
- `src/openai_api_tool/output.py`: stdout contract (one JSON object)
- `src/openai_api_tool/audit_log.py`: JSONL audit log (redaction)
- `tests/`: unit tests (prefer mocks, no real network)

## Add a read command

1) Create `src/openai_api_tool/commands/<name>.py`.
2) Implement `cmd_<name>(args, ctx) -> int`.
3) Register in `cli.py`.
4) Emit exactly one JSON object in JSON mode.
5) Add a unit test for output shape.

## Add a write command (safe pattern)

Rules:
- Dry-run by default (no writes without `--apply`).
- Batch/destructive writes require `--apply --yes`.
- writes must include `no_snapshot_available` `before_state` and require explicit no-snapshot approval before provider HTTP.
- Refuse when unsure.

Recommended workflow:
- plan (dry-run) -> review -> apply attempt -> explicit no-snapshot approval

Recommended v2 flags (when the command supports them):
- `--plan-out <path>` (save plan for review)
- `--plan-in <path>` (apply from a reviewed plan)
- `--receipt-out <path>` (save receipts for commands that really run; missing-approval write refusals create only refusal output when approval is missing)

Add tests for:
- refusal without `--apply`
- refusal without `--yes` for risky writes
- refusal before provider HTTP when before-state support is missing

## Run history (recommended)

This template auto-saves proof artifacts for write-capable commands under:
- `.state/runs/<run_id>/`

When adding new commands:
- Mark the CLI parser with `write_capable=True` so run history is enabled by default.
- Keep outputs deterministic and ensure plans/refusals/receipts never include secrets.

## Review prompts (recommended, optional)

Ship prompts to help users review plans and receipts safely:
- `docs/plan_review_prompt.md`
- `docs/receipt_review_prompt.md`
