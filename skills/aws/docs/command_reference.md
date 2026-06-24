# Command reference

Use this technical page after you know the AWS account, region, service, and operation you want. For choosing what to inspect first, start with the use cases and quickstart.

For the guided path, start with [Choose useful AWS tasks](use_cases.md), [Set up AWS access locally](onboarding.md), and [Understand safety and approvals](safety_model.md).

## Local commands

- `qwayk-aws-safe-agent-cli --output json --version`
- `qwayk-aws-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-aws-safe-agent-cli --output json auth check`
- `qwayk-aws-safe-agent-cli inventory summary`
- `qwayk-aws-safe-agent-cli runs list [--limit 20]`
- `qwayk-aws-safe-agent-cli runs show --run-id <run-id>`

## AWS service commands

Each service in the pinned Botocore inventory becomes a named subcommand. Each operation under that service also becomes a named command.

```bash
qwayk-aws-safe-agent-cli <service> <operation> [--input-json JSON_OR_PATH] [--output-file PATH]
```

Common read examples:

```bash
qwayk-aws-safe-agent-cli iam list-users
qwayk-aws-safe-agent-cli ec2 describe-instances
qwayk-aws-safe-agent-cli s3 list-buckets
```

Other useful first reads depend on your permissions:

- IAM access review: `iam list-users`, `iam list-roles`, `iam list-policies`
- EC2 review: `ec2 describe-instances`, `ec2 describe-security-groups`
- S3 review: `s3 list-buckets`, then bucket-specific reads when you know the bucket name
- Logging review: CloudTrail, CloudWatch, Config, Health, or GuardDuty read operations
- Spend review: billing, budgets, Cost Explorer, service quota, or capacity-related read operations

Example dry-run write plan:

```bash
qwayk-aws-safe-agent-cli iam create-user --input-json '{"UserName":"reporting-bot"}' --plan-out plan.json
```

The tool validates `--input-json` against the pinned Botocore model for that service operation. You can pass JSON text or a path to a JSON file.

## Safety flags

- Reads run without `--apply`.
- Dry-run writes omit `--apply` and can use `--plan-out <path>`.
- Live writes need `--apply --plan-in <path> --yes`.
- Add `--ack-no-snapshot` when the write cannot capture a reliable before-state or generic read-back. This is normally required for generated AWS writes.
- Add `--ack-irreversible` for delete-like or other hard-to-undo changes.
- Use `--receipt-out <path>` to save the live apply receipt.
- Use `--log-file <path>` if you want a second redacted audit log.
- Use `--output-file <path>` when the AWS response returns binary data.

## Shared flags

- `--env-file <path>`: local AWS settings file, default `.env`
- `--config <path>`: optional project defaults JSON
- `--project-dir <path>`: project root for local config
- `--run-id <id>`: use a specific local run id
- `--artifacts-dir <path>`: write run proof somewhere else
- `--no-artifacts`: disable local run proof
- `--output text`: human-readable output instead of JSON

## How to find operations

Use `inventory summary` to confirm the pinned coverage counts, then use service help for the command family you need:

```bash
qwayk-aws-safe-agent-cli iam --help
qwayk-aws-safe-agent-cli ec2 --help
qwayk-aws-safe-agent-cli s3 --help
```

For the full coverage boundary, use [Check the pinned coverage boundary](api_coverage.md).
