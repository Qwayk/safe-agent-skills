# Command guide

The CLI has 474 fixed provider commands. Use the inventory helpers to inspect exact paths, parameters, body shape, scopes, region, access gates, and safety before running one.

## Inventory and setup

```bash
qwayk-xero-safe-agent-cli --version
qwayk-xero-safe-agent-cli onboarding
qwayk-xero-safe-agent-cli inventory summary
qwayk-xero-safe-agent-cli inventory list --spec accounting --limit 50
qwayk-xero-safe-agent-cli inventory show --command accounting.get-invoices
```

## Auth and tenant commands

```bash
qwayk-xero-safe-agent-cli auth start --command accounting.get-invoices
qwayk-xero-safe-agent-cli auth exchange --code-file .state/oauth/code.txt --state returned_state
qwayk-xero-safe-agent-cli auth refresh
qwayk-xero-safe-agent-cli auth status --profile pkce
qwayk-xero-safe-agent-cli auth client-credentials --profile custom --scope accounting.settings.read
qwayk-xero-safe-agent-cli auth client-credentials --profile app-store --scope marketplace.billing
qwayk-xero-safe-agent-cli auth client-credentials --profile app-store --scope app.connections

qwayk-xero-safe-agent-cli tenant list
qwayk-xero-safe-agent-cli tenant select --tenant-id exact_id --region AU
qwayk-xero-safe-agent-cli tenant custom-discover
qwayk-xero-safe-agent-cli tenant show --profile pkce
qwayk-xero-safe-agent-cli tenant show --profile custom
```

## Fixed provider command shape

Every provider command is `<family>.<operation>`. Its optional `--input` file is one JSON object with only these sections:

```json
{
  "path": {},
  "query": {},
  "headers": {},
  "body": {},
  "file_path": "",
  "media_type": ""
}
```

Only sections documented for that command are accepted. Unknown path, query, header, and top-level body fields fail before any provider request. File commands use `file_path`; JSON commands use `body`.

Examples:

```bash
qwayk-xero-safe-agent-cli accounting.get-invoices --input examples/get-invoices.json
qwayk-xero-safe-agent-cli payroll-au.get-employees
qwayk-xero-safe-agent-cli projects.get-project --input examples/get-project.json
```

## Reads

Reads run immediately after auth, scope, region, tenant, and input checks. Use `--protected-output path` when you need the full financial, bank, payroll, tax, contact, file, or billing response. Normal stdout stays redacted.

## Writes

All non-GET provider operations create a plan unless `--apply` is present. A live apply needs the exact saved plan and `--approve`. Financial, payroll, bank, destructive, bulk, file, auth, billing, legal, tax, employment, and similar effects also need `--approve-high-risk`. A plan without a reliable before-state also needs `--ack-no-snapshot`.

Global flags must appear before the fixed command:

```bash
qwayk-xero-safe-agent-cli \
  --plan-out .state/plans/change.json \
  accounting.create-invoices \
  --input examples/create-draft-invoice.json

qwayk-xero-safe-agent-cli \
  --apply --approve --approve-high-risk --ack-no-snapshot \
  --plan-in .state/plans/change.json \
  --receipt-out .state/receipts/change.json \
  accounting.create-invoices
```

When Xero documents `Idempotency-Key`, use global `--idempotency-key value` during planning. If omitted, the plan creates and preserves one for supported writes.

## Families

Fixed commands cover `accounting`, `assets`, `bank-feeds`, `files`, `finance`, `identity`, `payroll-au`, `payroll-au-v2`, `payroll-nz`, `payroll-uk`, `projects`, `app-store`, and `einvoicing`. The exact list and classifications live in [API coverage](api_coverage.md).

`identity.get-connections` is a non-tenanted client-credentials command. It requires the `app.connections` scope plus an exact `Xero-Tenant-Id` or `Xero-User-Id` input header.

The four `app-store.*` commands use the separate `marketplace.billing` client-credentials path and retain their AU, NZ, and UK region classification. They are legacy transition commands, not a normally available billing service: Xero deprecated XASS in March 2026, accepted no new apps after 4 December 2025, and required existing customers to migrate by 1 July 2026. The endpoints remain in the pinned and current API reference, but live entitlement and behavior are unverified.
