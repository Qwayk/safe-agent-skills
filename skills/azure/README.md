# Azure

Put an agent on real Azure review work without handing it a blank API key and hoping it guesses the right thing. This skill gives the agent a controlled way to inspect Azure resources, explain what looks risky, and prepare changes you can approve before anything live happens.

Use it when you want help with questions like: what is running in this subscription, what is exposed publicly, which role assignments look too broad, which storage or network settings need review, and what change plan should be checked before someone applies it.

The important difference is control. A generic Azure helper is usually about reaching the API. This safe skill is about keeping the agent inside named Azure commands, starting with reads, separating writes into reviewed plans, redacting secret-like values, and leaving plans or receipts you can check later.

A useful first ask:

```text
Use the Azure skill to inspect this subscription, flag public exposure, broad access, and spend-sensitive resources, then stop before making any live change.
```

## What You Can Ask It To Do

- Map subscriptions, resource groups, and resource state before you decide what to touch.
- Find public exposure in storage, networking, and reachable resources.
- Review role assignments and other access settings that could be too broad.
- Look for cost-sensitive resources, quota-sensitive areas, and cleanup candidates.
- Inspect data-plane objects when a management-plane read is not enough.
- Turn a proposed change or batch input into a dry-run plan you can review first.
- Keep local records so another person can see what was planned, refused, or applied.

## Why This Skill Is Different

Azure is not a small account API. It can control production apps, identity, networking, databases, secrets, quotas, and spend. That is why this skill does not let the agent improvise endpoints or blend reads and writes in one loose step.

It uses explicit commands generated from the official Azure REST API specs. Read commands can run as normal checks. Write commands are plan-first: the tool writes a plan, you review the target and risk, and only then can the agent apply the saved plan with the required approval flags.

For higher-risk Azure work, the tool asks for stronger approval instead of pretending every write is the same. Secret-like read values are redacted by default, and the run can leave a local plan, receipt, refusal reason, or run-history record.

## Good First Jobs

Start with reads and summaries. These are the kinds of asks that fit the skill well:

```text
Check which subscription this token can read and stop before any change.
```

```text
List resource groups and flag public, expensive, or security-sensitive resources.
```

```text
Review role assignments for broad access and prepare a summary only.
```

```text
Create a dry-run plan for these Azure changes from my input file, but do not apply it.
```

A good answer should tell you which subscription or resource group was checked, which command ran, whether it was read-only, what looked risky, and whether the agent stopped before a live change.

## Install

Install slug:

```text
azure
```

Ask your agent to install the `azure` skill from `Qwayk/safe-agent-skills`.

If your host needs a command, run:

```bash
npx skills add Qwayk/safe-agent-skills@azure -g -y
```

## Access You Need

You need an Azure bearer token for the tenant and subscription you want to inspect.

Set these locally in the tool environment:

```bash
AZURE_API_TOKEN=<your-token>
AZURE_MANAGEMENT_ENDPOINT=https://management.azure.com
```

For data-plane commands, also set the service endpoint:

```bash
AZURE_DATA_PLANE_ENDPOINT=<service-endpoint>
```

You can limit where the tool is allowed to operate with optional allowlists:

```bash
AZURE_ALLOWED_TENANTS=
AZURE_ALLOWED_SUBSCRIPTIONS=
AZURE_ALLOWED_RESOURCE_GROUPS=
AZURE_ALLOWED_LOCATIONS=
AZURE_ALLOWED_SERVICES=
```

Keep `.env`, token files, and subscription secrets private. Do not paste bearer tokens into chat.

## First Safe Check

Start with local setup and inventory. These do not change Azure:

```bash
qwayk-azure-safe-agent-cli onboarding
qwayk-azure-safe-agent-cli auth check
qwayk-azure-safe-agent-cli inventory summary
```

Then run one small read with a real input file:

```bash
qwayk-azure-safe-agent-cli <service-command> <read-operation-name> \
  --input-json read.json
```

If you are not sure which service command fits, ask the agent to inspect the command catalog first and run only a read.

## How Changes Work

Writes are review-first.

First, create a plan:

```bash
qwayk-azure-safe-agent-cli <service-command> <write-operation-name> \
  --input-json change.json \
  --plan-out plan.json
```

Then review the target, request body, risk class, and expected effect.

Only after review, apply from the saved plan:

```bash
qwayk-azure-safe-agent-cli --plan-in plan.json --apply --yes \
  <service-command> <write-operation-name> \
  --input-json change.json
```

Some operations need extra acknowledgement before the tool will send the live request:

```bash
--ack-no-snapshot
--ack-irreversible
```

The tool refuses the live write if the required plan, apply flags, approval flags, or risk checks are missing. Azure rollback is not automatic, so the plan and receipt are the record to review.

## Coverage

The command catalog is built from a pinned official Azure REST API spec snapshot.

- 340 Azure service commands.
- 26,337 selected operations from 214,231 operation candidates.
- 20,673 management-plane operations and 5,664 data-plane operations.
- 12,904 read operations and 13,433 write operations.
- 411 sensitive read operations with default value redaction.
- Stable and preview Azure specs are included, with lifecycle noted in the coverage docs.
- Scope is official Azure `resource-manager` and `data-plane` specs only.

This is Azure cloud REST API coverage. It does not cover Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, Dynamics, Power Platform, Xbox, or other separate Microsoft products.

## Proof And Limits

The local proof shows that the command catalog is generated from the pinned Azure REST API specs, local startup works, auth readiness is reported, write gates exist, sensitive-read redaction is covered, and checked-in examples are redacted.

Live Azure behavior is still unverified in this repo snapshot without safe Azure credentials and safe targets. That means local checks can prove command shape and safety behavior, but they do not prove every command's real Azure response path.

Do not treat a live change as proved unless you have a receipt from the real target and have checked the result in Azure.

## Records Left Behind

Runs can leave local evidence such as:

- dry-run plan JSON
- live apply receipt JSON
- run history under `.state/runs/`
- refusal reasons when the tool blocks an unsafe or incomplete request
- redacted example output under `docs/examples/`

## Read More

- [Use cases](docs/use_cases.md)
- [Onboarding](docs/onboarding.md)
- [Quickstart](docs/quickstart.md)
- [Safety model](docs/safety_model.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)
