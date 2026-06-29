# Zapier

**Capability:** Work with Zapier partner automation APIs through named, reviewable commands.

Zapier can connect one product to thousands of apps, which is powerful and also easy for a generic agent to misuse. This skill gives an agent a safer way to inspect apps, actions, Zaps, authentications, trigger inboxes, promotions, and AI Actions before it prepares any live change.

You can ask the agent to find useful apps and actions, check what Zaps or action runs exist, review trigger inbox messages, prepare an action run, or draft a new Zap creation plan. The agent does not get a raw API bridge. It can only use the explicit commands generated from the pinned Zapier OpenAPI specs.

Safe means reads run first, writes create a plan by default, high-risk work needs a reviewed `--plan-in`, and destructive, send, auth, execution, or no-snapshot actions need extra approval. Tokens and private action inputs are redacted from output, plans, receipts, and local run records.

A useful first ask is: "Check my Zapier account and list the apps, actions, Zaps, and authentications you can see. Do not change anything. Then tell me what plan you would prepare next."

## Start here first

```bash
qwayk-zapier-safe-agent-cli onboarding
qwayk-zapier-safe-agent-cli --output json auth check
qwayk-zapier-safe-agent-cli --output json partner get-v2-apps
```

## What this skill helps with

- Find Zapier apps, categories, Zap templates, available actions, inputs, choices, and output fields.
- Review user profile, authentications, Zaps, Zap runs, action runs, trigger inboxes, and trigger messages.
- Prepare reviewed plans for creating Zaps, creating authentications, running actions, changing inboxes, managing promotions, and creating or executing AI Actions.
- Keep local plan and receipt files so a person can review what the agent intended and what happened after approval.

## Why this skill is different

Zapier actions can send messages, update CRMs, create records, trigger workflows, and touch connected apps the user may not be thinking about. A generic agent with direct API access can jump from "find the right action" to "run it" too easily.

This skill keeps the agent inside a fixed operation table. It can discover, inspect, and prepare changes, but live writes require plan review and explicit approval. It also separates ordinary reads from high-risk operations like action execution, Zap creation, authentications, inbox acknowledgement, and AI Action execution.

## What access this skill needs

Use a Zapier bearer token for normal API work. Some partner or White Label flows may also need a client ID, client secret, JWT, partner access, or specific OAuth scopes from Zapier. Keep all secrets in `.env`; never paste them into chat.

## Install and first run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-zapier-safe-agent-cli --output json onboarding
```

## How this skill stays safe

Reads run directly. Writes create plans unless `--apply` is used, and high-risk applies require `--plan-in` plus `--yes`, `--ack-irreversible`, or `--ack-no-snapshot`. The tool redacts secrets, stores local run records for write-capable commands, and writes receipts when live changes are applied.

## What it covers today

The pinned source covers 62 official operations: 21 Partner/Workflow API operations, 13 Trigger Inbox API operations, 3 Promotions API operations, and 25 AI Actions API operations. The full operation list is in the coverage map.

## What happens before live changes

For a write, the agent first produces a dry-run plan showing the exact operation, target path, body hash, credential fingerprint, risk level, and approval instructions. Live apply runs only after the plan is reviewed and passed back with the required approval flags. When Zapier does not expose a safe before-state snapshot, the user must acknowledge the no-snapshot risk before apply.

## Limits

This is not Zapier MCP setup, not the Zapier Platform integration builder, and not a free-form "call any Zapier endpoint" tool. Live behavior is not proved without real Zapier credentials and the needed partner access, so proof documents mark those paths as local and schema-verified only.

## Helpful docs

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Safety model](docs/safety_model.md)
- [Coverage map](docs/api_coverage.md)
- [Proof and checks](docs/proof.md)
