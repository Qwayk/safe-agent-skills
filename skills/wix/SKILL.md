---
name: wix
description: "Check Wix sites, products, bookings, and contacts. Preview changes for approval and verify what Wix saved."
---

# Wix

Use [Quickstart](docs/quickstart.md) and [Connect Wix](docs/onboarding.md) to find the right account or site. Use `wix-safe-agent-cli auth check` with the intended settings file. Confirm the target before proposing a change. Use only the named commands in [Commands](docs/command_reference.md) and keep keys, tokens and sign-in codes private.

For a change, use `--plan-out` and show the user what the plan would do. Apply the reviewed plan with `--plan-in --apply --yes` and any additional approval flags listed for the command. Read the receipt, including any refusal or follow-up it points to. See [Approvals and receipts](docs/safety_model.md).

The tool can read or change data that Wix exposes through its API. Work that needs Wix Editor, an unsupported API, or another permission needs the right route before it can go ahead. Use [API coverage](docs/api_coverage.md) to check.
