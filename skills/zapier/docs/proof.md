# Proof and verification

## November 22, 2026 checks

Both local copies passed 31 tests and ran from a fresh install outside the checkout. The install includes the operation list, and the source archive includes the skill and guides. All 62 command names are still available in help.

Tests used simulated Zapier replies. They covered a blank token and settings paths with spaces, the profile and app reads, the 27 commands that stop locally, and an action receipt that shows how to check the run. The approval tests check that a missing plan, missing acknowledgement, or changed request stops the write before it reaches Zapier.

To run the source tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -q
```

## June 29, 2026 checks

- Date (UTC): 2026-06-29
- Tool version: 0.1.0
- Provider API version: Partner API 2024.11.0 (OpenAPI 3.1.0)
- Added docs/specs:
  - `docs/specs/zapier_partner_api.yaml`
  - `docs/specs/zapier_trigger_inbox_api.yaml`
  - `docs/specs/zapier_promotions_api.yaml`
  - `docs/specs/zapier_ai_actions_api.json`
  - `docs/specs/zapier_docs_llms.txt`

### What the June tests checked

- Explicit command surface: 62
- Reads can run directly.
- Write operations default to dry-run with plan output.
- High-risk write operations require `--apply` and `--plan-in` plus ack/consent flags.
- Plans and receipts are written when requested via `--plan-out`/`--receipt-out`.
- `--apply --plan-in` now refuses if plan mismatches current command across operation, method, path, base URL, path params, query, body hash/presence, risk level, or credential fingerprint before any request is sent.
- Credential fingerprints are stable secret-safe hashes, so same-auth-type token swaps are detected without printing the token.
- Raw `--body-json` values are redacted in command strings across stdout, generated plans, generated receipts, summary text, run index rows, and audit rows.
- Provider failures, env-file config failures, and missing or invalid `--config` project files return one redacted JSON object in `--output json` mode.
- Auth and error outputs are JSON and do not print secrets.
- Required query parameters use the documented CLI flag spelling, such as `--client-id`.
- Audit log handles close cleanly after command execution.

See:
- `tests/test_command_inventory.py` (command count and surface)
- `tests/test_operation_safety.py` (dry-run + full plan-in mismatch refusal + plan/receipt structure)
- `tests/test_run_artifacts.py` (run summary/index/audit body redaction)
- `tests/test_auth_and_secrets.py` (auth checks, redacted provider/config errors, and leakage)
- `tests/test_cli_json_parse_errors.py` (parse errors and `--config` project file error shape)

### June test commands

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-zapier-safe-agent-cli --version
PYTHONPATH=src python3 -m unittest discover -s tests -q
git diff --check -- .
rg -n "[ \t]$" .
rg -n "^(<<<<<<<|=======|>>>>>>>)" .
```

Latest results on 2026-06-29:

- Latest unit suite for this source tool: 30 tests passed.
- `git diff --check` for scoped paths: clean.
- Editable install: passed.
- Console command version smoke: passed and returned `0.1.0`.
- Diff whitespace check: passed.
- Direct trailing-whitespace and conflict-marker scans over the source folder and source docs: passed after one trailing-space cleanup.

## Live account checks

Live account behavior still needs testing with a real Zapier token and the access each command requires.
