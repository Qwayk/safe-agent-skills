---
name: aws
description: Inspect AWS identity, resources, and reviewed change plans with account and region guardrails.
---

# Skill: AWS Safe Agent CLI

Use this skill when the user wants an agent to check AWS resources or prepare an AWS change without guessing the account, region, or risk.

The safe order is AWS identity first, read before planning, plan before apply, and receipt after any live attempt.

## Core rules

- Never ask the user to paste AWS access keys, secret keys, session tokens, or `.env` contents into chat.
- Start with `qwayk-aws-safe-agent-cli --output json --version`.
- Run `qwayk-aws-safe-agent-cli --output json auth check` before any non-STS AWS service call.
- If the user is not sure what to inspect, use `inventory summary` and the command reference before choosing a service command.
- Prefer safe reads first: IAM listing, EC2 inventory, S3 bucket settings, billing or quota checks, CloudWatch or CloudTrail lookups.
- Keep writes dry-run first.
- Live writes need a reviewed `--plan-in`, `--apply`, and `--yes`.
- Generated AWS writes normally need `--ack-no-snapshot` because the generic Botocore path cannot save a reliable before-state or infer a safe read-back for every operation.
- Delete-like or hard-to-undo writes need `--ack-irreversible`.
- Read the receipt verification block after apply. `limited` means the reviewed plan matched and the SDK response was captured; it does not mean AWS resource state was read back.
- Use `--output-file` for binary or sensitive payload responses.

## Good first asks

- "Check my AWS identity and region, then stop."
- "Show IAM users and access keys we should review before making changes."
- "List EC2 instances in this region and flag likely spend risk."
- "Review S3 bucket settings before I ask for any policy change."
- "Prepare a dry-run plan for this AWS change and explain the approval flags."

## Setup

Keep setup local:

- `AWS_DEFAULT_REGION` names the intended region.
- `AWS_PROFILE` points to a named local profile when needed.
- `AWS_ALLOWED_ACCOUNTS` lets the tool refuse the wrong AWS account.
- `AWS_ALLOWED_REGIONS` lets the tool refuse the wrong region.

Do not print or summarize secret credential values.

## Safe workflow

1. Verify the tool exists:

```bash
qwayk-aws-safe-agent-cli --output json --version
```

2. Verify AWS identity:

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
qwayk-aws-safe-agent-cli <service> <operation> --input-json '<json>' --plan-out plan.json
```

6. Apply only after review:

```bash
qwayk-aws-safe-agent-cli <service> <operation> --apply --yes --plan-in plan.json
```

7. Add extra safety flags only when the reviewed plan calls for them:

- `--ack-no-snapshot` for no-before-state writes
- `--ack-irreversible` for delete-like or hard-to-undo actions
- `--output-file <path>` for binary results

## Refusal conditions

- Missing AWS credentials, profile, region, or permission for the requested action
- Account or region does not match the configured allowlists
- Write requested without a dry-run review step
- Apply requested without a reviewed plan
- Current write apply needs `--ack-no-snapshot` or `--ack-irreversible`
- Binary result requested without `--output-file`

## Helpful docs

- Tool docs hub: `../../docs/README.md`
- Safety model: `../../docs/safety_model.md`
- Proof and examples: `../../docs/proof.md`
