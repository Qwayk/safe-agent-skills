---
name: azure
description: Use when the user wants to check Azure subscriptions, resources, access or costs, or plan and apply an approved Azure change.
---

# Azure

1. Check the install with `qwayk-azure-safe-agent-cli --output json --version`. Run `qwayk-azure-safe-agent-cli --output json auth check`. Confirm the target tenant and subscription. Use the local Azure CLI sign-in or the user’s private token settings.
2. Run one read the user can check, such as listing resource groups in the intended subscription. Use the named commands for Azure access, networks, resources and services. Leave tokens, private settings and secret values out of chat.
3. For a change, use `--bind-azure --plan-out plan.json`. Show the exact resource, changes, risks, likely costs and how you’ll confirm the result. Wait for approval.
4. Apply with the same input and `--plan-in plan.json --apply --yes`. Add `--ack-no-snapshot`, `--ack-irreversible` or `--ack-spend-money` where required and covered by the approval.
5. Read the receipt and confirm the resource when you can. If Azure is still working or a reply was lost, check the operation or resource before retrying.

Stop if the target or sign-in is unclear, Azure refuses access, or the target falls outside the configured lists. An offline preview and a simulated reply show how the tool works. A real Azure read checks account access.

[Setup](docs/onboarding.md) · [Commands](docs/command_reference.md) · [Approval steps](docs/safety_model.md) · [Test results](docs/proof.md)
