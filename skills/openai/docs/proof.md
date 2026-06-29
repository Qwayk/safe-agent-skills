# Proof and verification

OpenAI proof should answer a simple question: what has actually been checked for models, files, batches, fine-tuning, vector stores, assistants, and generated API calls, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check read examples, generated API plans, and write refusals before trusting OpenAI account work.

## Last verified

- Date (UTC): 2026-06-29
- Verified by: Codex builder refresh
- Tool version: 0.1.0
- Provider API version (if applicable): documented OpenAI OpenAPI spec `2.3.0`, refreshed 2026-06-29
- Environment: plan-only / base URL: https://api.openai.com/v1
- Tests: local unit suite passed (`41 tests, OK`); coverage and saved example output both matched the 273-operation pinned inventory. Live OpenAI behavior remains unverified without a real API key.

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `openai-api-tool --output json --version`

3) Auth/config check (read-only):
- `openai-api-tool --output json auth check`

4) One representative read query:
- `openai-api-tool --output json api ListContainers`

## 2026-06-29 refresh checks

- `python3 src/openai_api_tool/scripts/refresh_official_inventory.py --date 2026-06-29` produced 273 operation rows from the documented OpenAI OpenAPI spec.
- `.venv/bin/python -m unittest -q` passed with 41 tests.
- Ordinary API writes now have a direct safety test proving `--plan-in` is required before apply.
- `docs/api_coverage.md` has 273 operation rows and matches `docs/official_operations_v1_2026-06-29.txt`.
- `docs/examples/outputs/api_ops_list.json` reports `count: 273` and matches the pinned inventory.
- Representative changed doc links were spot-checked; rows without a proved method-page link fall back to the official API reference overview.

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/api_ops_list.json` (273 pinned operations from the 2026-06-29 documented OpenAPI refresh)
- `docs/examples/plan.example.json`
- `docs/examples/plan_spend_money.example.json` (spend-money plan with `classification.gates.plan_in/yes/ack_spend_money = true`; ordinary writes also require `plan_in`)
- `docs/examples/receipt.example.json`

## What can go wrong

- **Invalid API key / wrong scopes** → rerun `openai-api-tool --output json auth check --live` so the tool actually calls `/models` and surfaces `ok=false` plus the error details; the offline-only run simply reports which fields are populated.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify writes require `--plan-in`, then require explicit no-snapshot approval before OpenAI API key use or HTTP when no saved snapshot is available.
- **Write recovery contract**: write plans include `before_state.status: no_snapshot_available` and `recovery` with `automatic_rollback: false`, empty `backups/snapshots`, and `rollback_plan: null` so no-restore behavior is explicit.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
