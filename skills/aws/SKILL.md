---
name: aws
description: Use when the user wants to inspect AWS access, resources, logs or costs, or plan and apply an approved AWS change.
---

# AWS

1. Check the install with `qwayk-aws-safe-agent-cli --output json --version`, then run `qwayk-aws-safe-agent-cli --output json auth check`. Confirm the account, role, region and whether the configured lists allow that target. Use the user’s local AWS profile, single sign-on or role. Keep keys, tokens and settings out of chat.
2. Start with a small read. Pick IAM users or roles, EC2 instances, S3 bucket settings, CloudTrail events, CloudWatch alarms, billing or quotas according to what the user needs. Use `inventory summary` to see the packaged command list offline. Say what the read found before suggesting a change.
3. For a change, use `--bind-aws --plan-out plan.json` to save a plan tied to the account, role and region. Show the exact target, input, likely costs, risks and how you’ll check the result. Wait for the user’s approval.
4. Apply with the same input and `--plan-in plan.json --apply --yes`. Use `--ack-no-snapshot`, `--ack-irreversible` and `--ack-spend-money` when the operation requires them and the user approved the risk. Save binary output to a private file with `--output-file`.
5. Read the receipt and check the resource when you can. If AWS is still working or the reply was lost, check the operation or resource before retrying. A limited receipt records the reply without claiming a resource check.

Stop if the account, role, region or resource is unclear, permissions block the action, or the target is outside the configured lists. Use only the listed commands. Keep the saved examples separate from actual AWS account evidence.

[Setup](docs/onboarding.md) · [Commands](docs/command_reference.md) · [Approval steps](docs/safety_model.md) · [Test results](docs/proof.md)
