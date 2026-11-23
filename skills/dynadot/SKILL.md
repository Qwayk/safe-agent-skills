---
name: dynadot-api-safe-cli
description: Check Dynadot domains, prices, availability, DNS, and transfers, or prepare a change for the user to approve.
---

# Dynadot

Use `dynadot-api-tool` for Dynadot API3. Start with what the user wants to check or change. Use the [named commands](docs/command_reference.md) and keep API keys and transfer codes out of chat.

For a new account, run `dynadot-api-tool --output json --env-file dynadot.env onboarding`. Give the user the path to fill in, then use the same settings file with `auth check`. For a longer domain search, use `domains availability`. Keep one domain per request on a Regular Account and report errors as unresolved. See [account setup](docs/onboarding.md).

For a write, save a plan with `--plan-out`. Show the account, exact domains, proposed change, price if money is involved, and what you can verify afterward. Ask for approval. Apply the same inputs with `--apply --yes --plan-in`, plus `--ack-irreversible` and `--ack-no-snapshot` where required. Use the reviewed account keys and the approved `--max-price` for registration or renewal. Keep transfer codes in a new private file with `--out` or `--secret-out` as the command requires.

Read the receipt after applying. Report which actions finished and what still needs checking. If Dynadot doesn't confirm a write, check the order or current state before repeating it. See [approval and receipt guidance](docs/safety_model.md).
