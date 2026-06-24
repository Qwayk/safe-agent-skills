# Quickstart

Start with one small AWS read you can verify by eye: prove the account and region, then inspect IAM users, EC2 instances, or S3 buckets before asking for any change.

Need more ideas? See [Choose useful AWS tasks](use_cases.md). Need setup help? See [Set up AWS access locally](onboarding.md).

A good first ask is:

> Check my AWS identity and region, list IAM users and EC2 instances if permissions allow, and stop before creating, updating, deleting, exposing, sending, moving, or spending anything.

## What you will do first

1. Make sure the local tool can run.
2. Confirm the AWS caller, account, and region.
3. Run one small read that should be easy to recognize.
4. Stop before any write, public exposure, data movement, identity change, or spend-related action.

## 1. Check the tool version

```bash
qwayk-aws-safe-agent-cli --output json --version
```

## 2. Check setup and identity

If this is a fresh machine, run onboarding first. Keep AWS access keys, secret keys, session tokens, and `.env` contents out of chat.

```bash
qwayk-aws-safe-agent-cli onboarding
qwayk-aws-safe-agent-cli --output json auth check
```

Stop here if the account id, caller ARN, or region is not what you expected.

## 3. Run one small first read

Start with a read that confirms you are looking at the right AWS account before you inspect larger areas.

```bash
qwayk-aws-safe-agent-cli iam list-users
```

If IAM is not allowed for this caller, use another small read that fits your permissions:

```bash
qwayk-aws-safe-agent-cli ec2 describe-instances
qwayk-aws-safe-agent-cli s3 list-buckets
```

After the read, ask the agent to summarize the account, region, result size, and any obvious risk in normal words.

## 4. Stop before anything risky

Ask for a reviewed plan before any action that can change AWS state, permissions, public access, spend, messages, data movement, secrets, or resource lifecycle.

When you want to prepare a change, generate a dry-run plan and stop:

```bash
qwayk-aws-safe-agent-cli iam create-user --input-json '{"UserName":"reporting-bot"}' --plan-out plan.json
```

Do not apply the plan until a reviewer has checked the account, region, service, operation, input, risk categories, and required acknowledgement flags.

## What a useful first result includes

A good first AWS result should make these things clear:

- which AWS account was checked
- which caller ARN and region were used
- whether account and region allowlists passed
- which read command ran
- whether the result looks empty, blocked, or unexpected
- what is safe to inspect next
- whether any plan, receipt, or saved output was written

## Where to go next

- For real examples, read [Choose useful AWS tasks](use_cases.md).
- For setup details, read [Set up AWS access locally](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
