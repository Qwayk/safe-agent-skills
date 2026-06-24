---
name: aws
description: Inspect AWS and prepare careful AWS changes with identity checks, dry-run plans, reviewed apply, and receipts.
---

# Skill: AWS Safe Agent CLI

Use this skill when the user wants an agent to inspect AWS or prepare a careful AWS change.

The safe path is identity first, read when possible, plan before write, and receipt after apply.

## Core rules

- Never ask the user to paste AWS secrets into chat.
- Start with `qwayk-aws-safe-agent-cli --output json --version`.
- Run `auth check` before any non-STS AWS service call.
- Use `inventory summary` or the command reference before guessing a command.
- Reads can run directly.
- Writes stay dry-run first.
- Live writes need a reviewed `--plan-in`, `--apply`, and `--yes`.
- Generated AWS writes normally need `--ack-no-snapshot` because the generic model path cannot save a before-state or infer a safe read-back.
- Irreversible writes need `--ack-irreversible`.
- Read the receipt verification block after apply. `limited` means the SDK response and reviewed plan were checked, but no resource read-back ran.
- Use `--output-file` for binary responses.

## Good first asks

- "Check my AWS identity and region, then stop."
- "List the safest read-only AWS checks for this account."
- "Review IAM users before I ask for any access change."
- "Prepare a dry-run plan for this AWS change and tell me the risk."

## Setup

Make sure `.env` has:

- `AWS_DEFAULT_REGION=...`
- `AWS_PROFILE=...` when you use a named profile
- `AWS_ALLOWED_ACCOUNTS=...` when you want account guardrails
- `AWS_ALLOWED_REGIONS=...` when you want region guardrails

## Safe workflow

1. Verify the tool exists:

```bash
qwayk-aws-safe-agent-cli --output json --version
```

2. Verify auth:

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

3. Find the shipped command you need:

```bash
qwayk-aws-safe-agent-cli inventory summary
qwayk-aws-safe-agent-cli --help
```

4. Run a read:

```bash
qwayk-aws-safe-agent-cli <service> <operation>
```

5. Preview a write:

```bash
qwayk-aws-safe-agent-cli <service> <operation> --plan-out plan.json
```

6. Apply only after review:

```bash
qwayk-aws-safe-agent-cli <service> <operation> --apply --yes --plan-in plan.json
```

7. Add extra safety flags when needed:

- `--ack-no-snapshot` for no-before-state writes
- `--ack-irreversible` for delete-like actions
- `--output-file <path>` for binary results

## Refusal conditions

- Missing AWS setup for the requested action
- Write requested without a dry-run review step
- Apply requested without a reviewed plan
- Current write apply needs `--ack-no-snapshot` or `--ack-irreversible`
- Binary result requested without `--output-file`

## Helpful docs

- Tool docs hub: `docs/README.md`
- Safety model: `docs/safety_model.md`
- Proof and examples: `docs/proof.md`
