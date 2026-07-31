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

## Write commands: plan then apply

```bash
namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --opt-out-of-lock true --locked true
namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-high-risk domains update --domain example.com --opt-out-of-lock true --locked true
```

Global safety flags come before the family and command, as shown above. Repeat the same command values during apply so the reviewed plan fingerprint and target still match.

## Spend command example

```bash
namebright-safe-cli --output json --plan-out plan.json purchase register --domain-name example.com --years 1 --category-id 1 --category-name STANDARD
namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-spend purchase register --domain-name example.com --years 1 --category-id 1 --category-name STANDARD
```

## Run history

- `namebright-safe-cli --output json runs list --limit 20`
- `namebright-safe-cli --output json runs show --run-id RUN_ID`

## Safety notes

- Reads run directly and do not change provider state.
- Writes require `--plan-out` first, then `--apply --yes --plan-in`.
- Apply checks required ack flags from the plan target (for example: `--ack-spend`, `--ack-high-risk`, `--ack-destructive`, `--ack-ownership`, `--ack-no-snapshot`, `--ack-irreversible`, `--ack-external-message`, `--ack-account-creation`).
- `--receipt-out` is required when `--no-artifacts` is used.
