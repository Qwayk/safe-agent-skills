---
name: jobber
description: Check Jobber clients, requests, quotes, jobs, visits and invoices. Show proposed changes for approval before applying them.
---

# Jobber

Use `qwayk-jobber-safe-agent-cli` with `--output json`. Start with `auth check` and confirm the intended company with `read account --selection "id name"`. If access is missing, use [Connect Jobber](docs/onboarding.md). Keep token values and OAuth codes out of chat.

Pick a named read from the [command guide](docs/command_reference.md). Use `schema summary` to check the installed command list. Webhook commands list topics and verify signatures locally.

For a write, show the saved preview and wait for approval. Apply with `--apply --yes --plan-in`. Add `--ack-no-snapshot` for high-risk changes without a saved copy of the previous state and `--ack-irreversible` for clearly irreversible changes. Review the receipt and check the record before repeating an unclear result. Token renewal also uses `--apply --yes`. [Approval and recovery](docs/safety_model.md)
