# Proof pack

Date (UTC): 2026-06-11

You do not need to run these commands yourself for normal use. They are here for auditing, verification, and proof.

## Verification status

- Scope: this environment.
- Local tests are real and green.
- Local command outputs are real command runs with no secrets.
- Live write proof intentionally requires explicit no-snapshot approval before Klaviyo HTTP when no saved snapshot is available.
- API coverage shipped: `308` stable operations, `87` beta operations excluded by product choice.
- Stable surface file: `docs/official_operations_v1_2026-05-25.json`.

## Local checks (no network needed)

From tool root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q  # 27 tests, OK
.venv/bin/klaviyo-safe-agent-cli --output json --version
.venv/bin/klaviyo-safe-agent-cli --output json onboarding --no-write-env
.venv/bin/klaviyo-safe-agent-cli --output json --env-file .env.example auth check
.venv/bin/klaviyo-safe-agent-cli --output json --env-file .env.example api ops list --method GET
.venv/bin/klaviyo-safe-agent-cli --output json --env-file .env.example api ops show --op get_accounts
```

## Example outputs committed

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/plan.example.json`
- `docs/examples/outputs/receipt.example.json` (current safe refusal example)

## What can go wrong

- 401/403 credentials:
  - Verify API key and endpoint access, then rerun `auth check`.
- Missing required inputs:
  - Provide required params with `--path`, `--query`, or `--body-json`.
- High-impact write safety gates:
  - Add `--plan-in` and `--yes` for risky writes. When no saved snapshot is available, reviewed apply also needs `--ack-no-snapshot`.
- Recovery support:
  - Current write applies emit a receipt after explicit no-snapshot approval.
  - The tool does not create snapshots, provider backups, or automatic rollback.
- 429/timeouts:
  - Add a longer `KLAVIYO_TIMEOUT_S` and smaller query scope.
- Plan/apply mismatch:
  - Verify `plan_hash` before future apply support.
