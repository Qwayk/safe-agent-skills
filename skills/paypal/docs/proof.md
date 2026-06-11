# Proof

You do not need to run these commands yourself.
They exist so a reviewer can see what is proved locally and what still needs real PayPal access.

## Last checked

- Date (UTC): `2026-06-04`
- Verified by: `Codex`
- Tool version: `0.1.0`
- Scope: local packaging, parser coverage, onboarding, dry-run planning, run-artifact history, runtime safety-gates alignment, explicit no-snapshot approval, and no-recovery contract proof
- Live PayPal auth and writes: not verified in this repo run because no real sandbox or live merchant credentials were stored here. Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP.

## What is proved locally

- The CLI starts and returns one JSON object in `--output json` mode.
- `onboarding --no-write-env` works without secrets.
- All 133 shipped PayPal commands parse with required flags.
- `docs/api_coverage.md` matches the shipped command ledger.
- The safety-gates column in `docs/api_coverage.md` matches runtime `require_yes` and `require_ack` behavior.
- Write commands preview before auth or network when `--apply` is missing.
- Write dry-run plans include explicit `before_state`, `verification_plan`, and `plan.recovery` with a clear no-recovery contract.
- Write apply requires explicit no-snapshot approval before PayPal auth or HTTP when command-specific saved snapshot support is not available.
- Commands that are risky now correctly refuse without confirmation flags, and the `--yes` requirement now covers risky non-delete actions as well as delete actions.
- No shipped PayPal command currently requires `--ack-irreversible`.
- Auth failures return a redacted `ToolError` shape.

## What is still live-unverified or account-gated

- A successful `auth check` against a real PayPal app
- Real PayPal reads and writes with merchant data
- Read-back verification after live writes
- Partner-gated or account-gated areas such as partner referrals, payouts, referenced payouts, and some disputes
- Transaction reporting paths that depend on live account data and permissions

## Local proof commands

Run inside the tool folder:

```bash
.venv/bin/python -m paypal_safe_agent_cli --output json --version
.venv/bin/python -m paypal_safe_agent_cli --output json onboarding --no-write-env
.venv/bin/python -m unittest -q tests.test_paypal_write_recovery_contract
.venv/bin/python -m unittest -q tests.test_api_coverage_alignment tests.test_command_families
.venv/bin/python -m unittest -q
```

2026-06-04 Codex validation: focused safety/coverage suite 8 tests OK; full suite 17 tests OK; docs formatting 1 test OK; version smoke passed; committed JSON examples parsed.

Representative dry-run proof:

```bash
tmpdir=$(mktemp -d)
cat > "$tmpdir/.env" <<'EOF'
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_CLIENT_ID=demo-client-id
PAYPAL_CLIENT_SECRET=demo-client-secret
PAYPAL_TIMEOUT_S=30
EOF
cat > "$tmpdir/order.json" <<'EOF'
{
  "intent": "CAPTURE",
  "purchase_units": [
    {
      "reference_id": "demo-order-1",
      "amount": {
        "currency_code": "USD",
        "value": "10.00"
      }
    }
  ]
}
EOF
.venv/bin/python -m paypal_safe_agent_cli --env-file "$tmpdir/.env" --output json orders create --body-file "$tmpdir/order.json" --plan-out "$tmpdir/plan.json"
.venv/bin/python -m paypal_safe_agent_cli --env-file "$tmpdir/.env" --output json --apply --yes --ack-no-snapshot payment-tokens delete --id paytok-demo-123
```

## Example outputs

Committed redacted examples:

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/onboarding.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; old filename kept)

Notes:

- `auth_check.json` is a real failure-shape example captured without valid PayPal credentials.
- `receipt.example.json` is a missing-approval refusal example. Approved supported writes emit receipts after explicit no-snapshot approval when no useful before-state can be saved.

## Main risks

- Wrong sandbox or live credential pair will make `auth check` fail.
- Some PayPal products need account approval or partner headers even when the endpoint is officially documented.
- A few PayPal query-style endpoints use `POST`; this tool keeps them read-only on purpose.

## Links

- Sources: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Build notes: `docs/engineering_notes.md`
