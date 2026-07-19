# Quickstart

Use this after [connecting Xero](onboarding.md). It proves the selected organisation can be read before you ask for any live change.

## Install from source

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
qwayk-xero-safe-agent-cli --version
```

## Inspect the fixed boundary without credentials

```bash
qwayk-xero-safe-agent-cli inventory summary
qwayk-xero-safe-agent-cli inventory show --command accounting.get-invoices
qwayk-xero-safe-agent-cli inventory list --spec payroll-au --limit 20
```

## Confirm local auth and target

```bash
qwayk-xero-safe-agent-cli auth status --profile pkce
qwayk-xero-safe-agent-cli tenant show
```

These status commands never print token values.

## First useful reads

```bash
qwayk-xero-safe-agent-cli accounting.get-organisations
qwayk-xero-safe-agent-cli \
  --protected-output .state/protected/invoices.json \
  accounting.get-invoices \
  --input examples/get-invoices.json
```

For commands that can return financial, bank, payroll, tax, contact, file, or billing data, normal JSON keeps the response shape but masks every provider value. `--protected-output` writes the full provider response to an owner-only local file and prints only its path, size, and hash.

## Prepare a write without applying it

```bash
qwayk-xero-safe-agent-cli \
  --plan-out .state/plans/create-draft-invoice.json \
  accounting.create-invoices \
  --input examples/create-draft-invoice.json
```

Review the saved plan. Creating an invoice has no reliable before-state, so apply also needs the no-snapshot acknowledgement:

```bash
qwayk-xero-safe-agent-cli \
  --apply \
  --approve \
  --approve-high-risk \
  --ack-no-snapshot \
  --plan-in .state/plans/create-draft-invoice.json \
  --receipt-out .state/receipts/create-draft-invoice.json \
  accounting.create-invoices
```

Do not run the apply command until the tenant, target, input, risks, and no-snapshot warning are correct.
