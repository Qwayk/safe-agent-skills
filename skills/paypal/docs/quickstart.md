# Quickstart

If you are non-technical, start with `use_cases.md` and `onboarding.md`.
This page is the technical setup and first-run guide.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## No-credential smoke check

These commands work before you have a real PayPal app:

```bash
qwayk-paypal-safe-agent-cli --output json --version
qwayk-paypal-safe-agent-cli --output json onboarding --no-write-env
```

## Configure `.env`

1. Copy `.env.example` to `.env`.
2. Set `PAYPAL_ENVIRONMENT=sandbox` while testing.
3. Add `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` from PayPal Developer Dashboard -> Apps & Credentials.
4. Leave `PAYPAL_API_BASE_URL` blank unless you have a special override.

Then run:

```bash
qwayk-paypal-safe-agent-cli --output json auth check
```

`auth check` needs a real PayPal app client ID and client secret. It is not expected to work against placeholder values in `.env.example`.

## First read commands

```bash
qwayk-paypal-safe-agent-cli --output json orders get --id ORDER-ID
qwayk-paypal-safe-agent-cli --output json webhooks list
qwayk-paypal-safe-agent-cli --output json invoicing templates-list
```

## First write preview

Create a JSON body file, then preview the write:

```bash
qwayk-paypal-safe-agent-cli --output json orders create --body-file order.json --plan-out plan.json
```

Review the plan, then request apply:

```bash
qwayk-paypal-safe-agent-cli --output json --apply orders create --body-file order.json --receipt-out receipt.json
```

Write apply requires explicit no-snapshot approval when command-specific saved snapshot support is unavailable; missing approval refuses before PayPal auth or HTTP. approved apply emits a receipt that records no-snapshot approval; missing approval creates only a refusal.

Write plans include `before_state` and a no-recovery contract, so expect no automatic rollback promise and no implied snapshot or backup, and no generated rollback plan.

Some higher-risk actions also need `--yes`:

```bash
qwayk-paypal-safe-agent-cli --output json --apply --yes payment-tokens delete --id PAYTOK-ID
qwayk-paypal-safe-agent-cli --output json --apply --yes disputes accept-claim --id DISP-ID
qwayk-paypal-safe-agent-cli --output json --apply --yes payments authorizations.void --authorization-id AUTH-ID
```

## Run history

Write-capable commands save local artifacts next to your `--env-file`:

```bash
qwayk-paypal-safe-agent-cli --output json runs list --limit 10
qwayk-paypal-safe-agent-cli --output json runs show --run-id 2026-05-26T080651Z_9d089b
```
