# Command reference

Use this page for exact NameBright command patterns.

## Get connected

- `namebright-safe-cli --output json --version`
- `namebright-safe-cli --output json onboarding`

## Check access

- `namebright-safe-cli --output json auth check`
- `namebright-safe-cli --output json auth token`

## Account and domain reads

- `namebright-safe-cli --output json account show`
- `namebright-safe-cli --output json purchase availability --domain-name example.com`
- `namebright-safe-cli --output json domains list`
- `namebright-safe-cli --output json domains get --domain example.com`
- `namebright-safe-cli --output json contacts get-all --domain example.com`
- `namebright-safe-cli --output json contacts get-registrant --domain example.com`
- `namebright-safe-cli --output json nameservers list --domain example.com`
- `namebright-safe-cli --output json host-records list-all --domain example.com`
- `namebright-safe-cli --output json inbound-push list-pending`
- `namebright-safe-cli --output json outbound-push list-pending`
- `namebright-safe-cli --output json whois-accuracy get --domain example.com`
- `namebright-safe-cli --output json contact-verification list --domain example.com`

## Prepare and apply a change

```bash
namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --opt-out-of-lock true --locked true
namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-high-risk domains update --domain example.com --opt-out-of-lock true --locked true
```

Put the global flags first. Use the same NameBright credentials, settings folder, and command values that you used to save the plan.

## Review a purchase

```bash
namebright-safe-cli --output json --plan-out plan.json purchase register --domain-name example.com --years 1 --category-id 1 --category-name STANDARD
namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-spend purchase register --domain-name example.com --years 1 --category-id 1 --category-name STANDARD
```

## Check an order

Use the order number from the receipt with the same account. A paid order can take time to appear.

```bash
namebright-safe-cli --output json orders get --customer-order-number EXAMPLE_ORDER
```

If NameBright is still creating the order, check again later. See the [approval guide](safety_model.md) before sending another purchase.

## Run history

- `namebright-safe-cli --output json runs list --limit 20`
- `namebright-safe-cli --output json runs show --run-id RUN_ID`

## Safety notes

- Reads run directly and do not change provider state.
- Writes require `--plan-out` first, then `--apply --yes --plan-in`.
- The plan lists the approvals it needs (for example: `--ack-spend`, `--ack-high-risk`, `--ack-destructive`, `--ack-ownership`, `--ack-no-snapshot`, `--ack-irreversible`, `--ack-external-message`, `--ack-account-creation`).
- Use a new receipt filename. Give `--receipt-out` when you use `--no-artifacts`.
