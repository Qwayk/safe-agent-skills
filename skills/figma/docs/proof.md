# Proof pack (local proof only)

## Purpose

This document is evidence of what is proven in this repository today for customer-facing claims.
All examples are from committed local artifacts and unit-test-backed runs. Live Figma
behavior is not yet verified in this environment because real provider credentials and
team/plan access are not available here.
You don't need to run these commands yourself. They exist for auditing and proof.

## Last verified (UTC)

- Date: `2026-06-04`
- Verified by: local tool runtime checks
- Tool version: `0.1.0`
- Provider API version: Figma REST docs references captured in `references.md`
- Environment: local stub/fixture outputs under `docs/examples`

## Local proof evidence (committed artifacts)

Use these files for review and copy/paste checks:

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/operations_list_files.json`
- `docs/examples/outputs/operations_show_post_comment.json`
- `docs/examples/outputs/get_file_nodes.json`
- `docs/examples/outputs/post_comment_dry_run.json`
- `docs/examples/outputs/post_comment_apply.json` (saved gate example before explicit no-snapshot approval)
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What each proof file shows

- `outputs/version.json` — CLI version surface and startup path.
- `outputs/auth_check.json` — auth status logic with token source and a successful live probe.
- `outputs/operations_list_files.json` — `operations list` filter behavior.
- `outputs/operations_show_post_comment.json` — metadata rendering for a write operation.
- `outputs/get_file_nodes.json` — explicit read execution with named flags and filtered query parameters.
- `outputs/post_comment_dry_run.json` — write path default behavior with request plan, no apply.
- `outputs/post_comment_apply.json` — saved gate example that shows the no-snapshot approval checkpoint before a live write.
- `plan.example.json` — reusable example write plan output.
- `receipt.example.json` — example receipt shape for reviewed applies; the runtime can also emit a real apply receipt after explicit no-snapshot approval.

## Local proof and test status

- Implementation coverage:
  - `operation_specs.py` to CLI runtime for explicit operation execution.
  - `operations` command parsing and request construction (`list`, `show`, explicit area/op execution).
  - auth/token behavior with `--skip-live` and auth mode checks.
  - write safety gates: dry-run default, `--apply`, `--yes`, `--ack-irreversible`, `--plan-in`, and `--ack-no-snapshot` when no saved snapshot exists.
  - output persistence with `--out` + `--overwrite`.
- Live-provider verification status:
  - **Not yet verified.** We only have local fixture/server evidence and mocked tests for endpoint request shape and safety behavior.
  - Current write applies require explicit no-snapshot approval before provider HTTP when no saved snapshot is available.

## What can still be wrong

- Endpoints that are documented but gated by plan/team/org settings may still return
  provider-level access errors in real projects.
- Read-after-write verification still depends on real provider access and the specific write family used.
- Discovery remains in runtime as docs-backed coverage (`/v1/discovery`) because the endpoint
  is missing from the published OpenAPI YAML.
