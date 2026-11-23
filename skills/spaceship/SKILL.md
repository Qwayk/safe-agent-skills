---
name: spaceship
description: Check Spaceship domains, prices, DNS, transfers, and SafePay. Prepare account changes for approval.
---

# Spaceship

Use the [named commands](docs/command_reference.md) on `https://spaceship.dev/api`. Start with a read that answers the request, such as `domains list` or `domains price`. Follow [account setup](docs/onboarding.md) if the key or settings file is missing.

Run `qwayk-spaceship-safe-agent-cli --output json` with the command you need. Keep keys, transfer codes, and payment details out of chat. Keep the approved request values in a private file.

1. Save a plan and show the user the account, target, price or fee split, and anyone the change will contact. Use the intended account before asking for approval. Follow the plan's approval flags, including `--ack-no-snapshot` if it applies.
2. After approval, use the same settings and request with `--apply --yes --plan-in`. Use a new receipt filename if you choose one.
3. Use an async ID to check an operation still processing. For SafePay, explain who still needs to confirm. If the reply is lost or the result is unclear, check Spaceship before making a new plan.

Use [Review a Spaceship change](docs/safety_model.md) for the full flow. Spaceship lists `domains delete <domain>` and `domains personal-nameservers get-host` as under development. Both commands stop locally with HTTP 501.
