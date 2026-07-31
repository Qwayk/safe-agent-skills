# Agent extension guide

Use this page when an AI coding assistant adds or changes commands in the source tool.

## Repo map

- `src/namebright_safe_cli/operations.py`: the fixed 61-operation registry and all command metadata
- `src/namebright_safe_cli/cli.py`: generates explicit family and command parsers from that registry
- `src/namebright_safe_cli/client.py`: reconstructs only registered requests and obtains in-memory OAuth tokens
- `src/namebright_safe_cli/workflow.py`: saved plans, snapshots, approvals, drift checks, writes, verification, and receipts
- `src/namebright_safe_cli/commands/`: local onboarding and auth-check handlers only
- `src/namebright_safe_cli/config.py`: `.env` parsing and validation
- `src/namebright_safe_cli/http.py`: fixed-host HTTP transport and bounded retry behavior
- `src/namebright_safe_cli/output.py`: stdout contract (one JSON object)
- `src/namebright_safe_cli/audit_log.py`: JSONL audit log (redaction)
- `tests/`: unit tests (mocked, no live network)

## Change the official boundary

Do not add a command from memory or introduce a generic request route. First update the pinned official coverage evidence. Then add or change the exact `OperationSpec` and typed fields in `operations.py`; the parser and registry-bound client use that metadata.

For a read, define its fixed method, path, fields, sensitive response fields, and pagination defaults. Test the parser leaf, registry dispatch, fixed host, response redaction, and coverage row.

For a write, also define its risk, required acknowledgements, before-state reads, no-snapshot status, outside-message effect, secret-file inputs, and fixed verification reads. Tests must prove planning sends no provider write, apply binds the exact plan and values, missing acknowledgements refuse before write, snapshots detect drift, secrets never enter artifacts, one write is sent, verification runs, and a redacted receipt is saved.

## Run history

Write-capable commands use `.state/runs/<run_id>/` for proof artifacts.
Keep run output deterministic and keep secrets and secret-file paths out of every plan, receipt, log, index, summary, and error.

Before handoff, run Ruff, mypy, the full Python 3.12 unit suite, source and wheel builds, archive inspection, and the clean installed-wheel checks documented in `docs/proof.md`.

## Review prompts

Use these prompt pages for manual review:
- `docs/plan_review_prompt.md`
- `docs/receipt_review_prompt.md`
