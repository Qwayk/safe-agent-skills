# Quickstart

Your first useful result is a list of the active domains in your SAV account:

```bash
sav --output json --env-file .env domains active
```

This read requires a SAV API key and an IP address that SAV has allowed. If those are not ready, follow [Onboarding](onboarding.md) first.

## Confirm the tool

```bash
sav --output json --env-file .env --version
```

## Try another read

```bash
sav --output json --env-file .env pricing list
```

The response is JSON. It names the command and official operation, then returns the redacted SAV response.

Transfer dry-runs must read the code from a private file. Create it without putting the code in the command itself:

```bash
mkdir -p .state/secrets
chmod 700 .state/secrets
AUTH_FILE="$(mktemp ".state/secrets/sav-transfer.XXXXXX")"
read -r -s SAV_TRANSFER_CODE
printf '%s\n' "$SAV_TRANSFER_CODE" > "$AUTH_FILE"
chmod 600 "$AUTH_FILE"
unset SAV_TRANSFER_CODE

sav --output json --env-file .env --plan-out .state/plans/submit-transfer-code.example.json domains submit-transfer-code --domain-name example.com --auth-code-file "$AUTH_FILE"

rm -f "$AUTH_FILE"
```

Apply runs from the reviewed plan and does not re-read a transfer file.

## Prepare a change without sending it

```bash
sav --output json --env-file .env --plan-out .state/plans/example-sale-price.json domains set-sale-price --domain-name example.com --sale-price 42
```

This creates a private mode-`0600` plan and makes no SAV request. The displayed plan hides sensitive values.

## Stop and review

Do not apply until the target, requested values, missing snapshot, and lack of rollback are clear. A reviewed apply repeats the exact command and values:

```bash
sav --output json --env-file .env --apply --yes --ack-no-snapshot --ack-high-risk --plan-in .state/plans/example-sale-price.json --receipt-out .state/receipts/example-sale-price.receipt.json domains set-sale-price --domain-name example.com --sale-price 42
```

The apply command is shown for reference. The source proof did not run it against SAV.
