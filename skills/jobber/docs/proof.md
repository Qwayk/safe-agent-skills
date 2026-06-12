# Proof and verification

This page is for trust and auditing. Most users will never need to run these commands themselves.

You don’t need to run these commands yourself. They are here so your reviewer can see what was checked and what should be left behind.

## What this page proves

- Tool install and output contract (`--output json`).
- OAuth auth check and token file status behavior.
- Read and write command behavior shape (plan first, apply second).
- Write plans and receipts now always include `snapshot_status` and recovery notes for no-snapshot mutations.
- High-risk no-snapshot writes require `--ack-no-snapshot` before live apply.
- Safety rails for jobs and webhook helpers.

## Ground rules

- Never include secrets in outputs or screenshots.
- Use redacted sample values in all shared output examples.
- Offline files in this repo are redacted examples and must stay local.

## Last verified

- Date (UTC): 2026-06-12
- Verified by: repository local validation
- Tool version: 0.1.0
- Provider API version: 2025-04-16 (`X-JOBBER-GRAPHQL-VERSION`)
- Environment: offline redacted examples
- Local test result: `python3 -m venv .venv && .venv/bin/python -m pip install -e . && .venv/bin/python -m unittest -q` passed with 59 tests.
- Repo audit result: tool workflow checks and alignment audits are passing in this repository.
- Diff hygiene result: `git diff --check` passed.

## Smoke checks (read-only and safe)

Run these when safe connectivity is available:

1) Basic tool and contract:
- `qwayk-jobber-safe-agent-cli --output json --version`
- `qwayk-jobber-safe-agent-cli --output json auth check`
- `qwayk-jobber-safe-agent-cli --output json schema summary`

2) Safe read example:
- `qwayk-jobber-safe-agent-cli --output json read clients --selection "nodes { id name } totalCount" --limit 10`

3) Safe write plan and apply gate:
- `qwayk-jobber-safe-agent-cli --output json --plan-out plan.json write clientCreate --args-json '{"input": {"firstName":"Sample","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'`
- `qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json write clientCreate --args-json '{"input": {"firstName":"Sample","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'`

3b) High-risk no-snapshot write requires manual ack:
- `qwayk-jobber-safe-agent-cli --output json --plan-out delete_plan.json write clientDelete --selection 'client { id }'`
- `qwayk-jobber-safe-agent-cli --output json --apply --yes --ack-no-snapshot --ack-irreversible --plan-in delete_plan.json write clientDelete --selection 'client { id }'`

4) Batch plan shape:
- `qwayk-jobber-safe-agent-cli --output json --plan-out jobs-plan.json jobs run --file examples/jobs_with_write.csv`

## Example outputs (redacted)

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What to inspect after a live run

- `runs list --limit 20`
- `runs show --run-id <run-id>`
- Saved plan and receipt file paths returned in command output.
- `docs/examples/plan.example.json` and `docs/examples/receipt.example.json` for format shape only.

## Links

- Sources used: [References](references.md)
- Coverage source of truth: [API coverage](api_coverage.md)
