# Command reference

See the [coverage table](api_coverage.md) for all 12 named commands.

- Host: fixed `https://api.sav.com/domains_api_v1`
- Requests do not follow redirects and are sent with a timeout policy (finite positive seconds only).
- Format: `sav [global flags] <section> <action> [command flags]`

Global flags used by every command:

- `--env-file` (optional; defaults to `.env`)
- `--output json`
- `--timeout-s` (finite positive number of seconds)
- `--plan-in` and `--plan-out` for write flow
- `--plan-out` must be a `.json` path

## Read commands

```bash
sav --output json --env-file .env domains active
sav --output json --env-file .env sales recent-auction
sav --output json --env-file .env sales recent-premium
sav --output json --env-file .env pricing list
```

## Prepare a write plan

```bash
sav --output json --env-file .env --plan-out .state/plans/remove-from-sale.example.json domains remove-from-sale --domain-name example.com
sav --output json --env-file .env --plan-out .state/plans/submit-transfer-code.example.json domains submit-transfer-code --domain-name example.com --auth-code-file "$AUTH_FILE"
sav --output json --env-file .env --plan-out .state/plans/set-auto-renewal.example.json domains set-auto-renewal --domain-name example.com --enabled 1
sav --output json --env-file .env --plan-out .state/plans/set-sale-price.example.json domains set-sale-price --domain-name example.com --sale-price 42
sav --output json --env-file .env --plan-out .state/plans/set-nameservers.example.json domains set-nameservers --domain-name example.com --ns-1 ns1.example.net --ns-2 ns2.example.net
sav --output json --env-file .env --plan-out .state/plans/set-privacy.example.json domains set-privacy --domain-name example.com --enabled 0
sav --output json --env-file .env --plan-out .state/plans/set-whois-contacts.example.json domains set-whois-contacts --domain-name example.com --name "Alice Example" --organization "Example LLC" --email-address alice@example.com --street "1 Example Way" --city Austin --country US --phone "+1-555-0100" --state TX --postal-code 78701 --update-registrant 1 --update-tech 0 --update-admin 0
sav --output json --env-file .env --plan-out .state/plans/list-external-sale.example.json domains list-external-sale --domain-name example.com --sale-price 12
```

## Apply examples (exact reviewed-flow)

Each apply example must keep root flags first and include all approvals:

```bash
sav --output json --env-file .env --apply --yes --ack-no-snapshot --ack-high-risk --plan-in .state/plans/set-sale-price.example.json --receipt-out .state/receipts/set-sale-price.example.receipt.json domains set-sale-price --domain-name example.com --sale-price 42
```

```bash
sav --output json --env-file .env --apply --yes --ack-no-snapshot --ack-high-risk --plan-in .state/plans/set-whois-contacts.example.json --receipt-out .state/receipts/set-whois-contacts.example.receipt.json domains set-whois-contacts --domain-name example.com --name "Alice Example" --organization "Example LLC" --email-address alice@example.com --street "1 Example Way" --city Austin --country US --phone "+1-555-0100" --state TX --postal-code 78701 --update-registrant 1 --update-tech 0 --update-admin 0
```

## Check the plan and receipt

Use a plan saved with the intended SAV key. Keep the same key and inputs during apply. Give an optional `--receipt-out` its own new file. See [approval and receipt rules](safety_model.md).

For a transfer, create a private code file using [Quickstart](quickstart.md). Pass it only while preparing the plan. During apply, use the reviewed plan file.
