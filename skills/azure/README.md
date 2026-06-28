# Azure

**Capability:** Reads + careful changes

Azure is where production apps, data, access, and spend live. This safe skill is for the moment you want an agent to help review an Azure subscription without giving it room to guess, skip review, or change live resources by accident.

Ask it to map what is running and find public exposure. It can review broad role assignments, check storage or network risk, flag expensive resources, and prepare careful change plans you can read first.

Instead of letting a generic agent improvise Azure API calls, it keeps the work inside explicit commands. The agent reads first, plans before writes, asks before risky actions, redacts secrets, and leaves receipts you can check.

A good first ask is: Check this Azure subscription for public exposure, broad access, and spend risk, then stop before any live change.

## Start here first

- Want ideas for real work? [What this skill can help you do](docs/use_cases.md)
- Need setup? [Set up your account step by step](docs/onboarding.md)
- Want the safety story first? [See how this skill keeps changes safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- See what is running in a subscription before you decide what to touch.
- Find public exposure in storage, networking, and reachable resources.
- Review role assignments and spot broad access that should be checked.
- Flag cost-sensitive resources and cleanup candidates.
- Prepare Azure change plans that stop for review before anything live changes.
- Keep local plans, receipts, and run history so the work can be checked later.

## Why this skill is different

Many Azure API helpers make it easy for an agent to call endpoints. That is not enough when the account contains production resources, customer data, identity rules, or spend controls.

This safe skill keeps the agent inside named commands generated from the official Azure REST API boundary. It starts with reads, shows plans before writes, asks for stronger approval on risky actions, redacts secrets from normal output, and leaves receipts so you can check what happened later.

That makes it better for real Azure account work than a generic API shortcut, especially when you want useful help from an agent but still need control over live infrastructure.

## What access this skill needs

- A Microsoft Entra bearer token for the Azure tenant and subscription you want to inspect.
- The normal Azure management endpoint, which defaults to `https://management.azure.com`.
- A data-plane endpoint only when you ask for a data-plane command.
- Optional allowlists for tenants, subscriptions, resource groups, locations, and service commands.

## Install and first run

Install slug: `azure`

Ask your agent to install the `azure` skill from `Qwayk/safe-agent-skills`.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@azure -g -y
```

Then try:

```text
Connect this skill to my Azure account and run the first safe inventory check. Do not apply any change.
```

## How this skill stays safe

- Safe checks can run without a live write approval.
- Live changes start as a dry-run plan.
- Riskier Azure changes need a reviewed plan and clear approval.
- High-risk or no-snapshot changes need an extra acknowledgement.
- Irreversible changes need one more acknowledgement.
- Secrets and tokens are redacted from normal output.

## What it covers today

- 340 service commands.
- 26,337 selected operations from 214,231 candidates.
- Inventory source pinned at `ada8601c3b75c15f06f21e50f9368d9476229305`.
- Coverage scope is official Azure `resource-manager` and `data-plane` specs only.
- Non-Azure Microsoft products are excluded (for example Graph, M365, Azure DevOps, GitHub, Xbox, Dynamics).

## What happens before live changes

- The agent creates a plan first.
- You review the target, operation, input, and risk.
- The live command must use the saved plan.
- The tool records a receipt after the provider responds.
- Generated Azure writes are marked live-unverified until real credentials and safe targets are available.

## What proof it leaves behind

- Local run history under `.state/runs/`.
- Plan files for dry-run writes.
- Receipt files for live applies.
- Redacted example files in `docs/examples/`.
- The pinned official inventory in `docs/official_inventory.json`.

## Limits

- This is for Azure cloud REST APIs only.
- It does not cover Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, Dynamics, Power Platform, or other separate Microsoft products.
- Data-plane commands need the right service endpoint.
- Live Azure account behavior remains unverified until safe credentials and targets are available.

## Helpful docs

- [Browse all docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
