# Quickstart

After [connecting your account](onboarding.md), try a read. The examples use `.env`. Use your own settings file if you chose a different name.

```bash
sav --output json --env-file .env domains active
sav --output json --env-file .env sales recent-auction
sav --output json --env-file .env sales recent-premium
sav --output json --env-file .env pricing list
```

## Prepare a change

For example, ask the agent to prepare a plan to turn on auto-renewal for a domain. This command saves the plan locally:

```bash
sav --output json --env-file .env --plan-out .state/plans/renewal.json \
  domains set-auto-renewal --domain-name example.com --enabled 1
```

Check the domain, the requested setting, and the account key used to prepare the plan. After approval, run with the same key and inputs:

```bash
sav --output json --env-file .env --apply --yes --ack-no-snapshot --ack-high-risk \
  --plan-in .state/plans/renewal.json \
  domains set-auto-renewal --domain-name example.com --enabled 1
```

The receipt shows what SAV returned. Read the [approval guide](safety_model.md) before applying or trying a change again.

## Prepare a pending transfer

Start with a regular file under a private folder. Enter the transfer code when prompted by your shell.

```bash
(umask 077; mkdir -p .state/secrets)
code_file="$(mktemp .state/secrets/sav-transfer.XXXXXX)"
read -r -s sav_transfer_code
printf '%s\n' "$sav_transfer_code" > "$code_file"
unset sav_transfer_code

sav --output json --env-file .env --plan-out .state/plans/transfer.json \
  domains submit-transfer-code --domain-name example.com --auth-code-file "$code_file"

rm -f "$code_file"
```

The file needs one non-empty line, mode `0600`, and a mode-`0700` parent folder. Use `--auth-code-file` only when making the plan. Apply uses the reviewed plan and keeps the code out of displayed output.

For nameservers, sale prices, privacy, and contact updates, see the [command reference](command_reference.md).
