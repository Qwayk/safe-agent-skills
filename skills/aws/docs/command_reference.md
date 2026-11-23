# Command reference

Find the operation you need in [API coverage](api_coverage.md). For a first read, follow [the quickstart](quickstart.md).

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

To save a plan for review, use:

```bash
qwayk-aws-safe-agent-cli iam create-user --input-json '{"UserName":"reporting-bot"}' --bind-aws --plan-out plan.json
```

The tool validates `--input-json` against the pinned Botocore model for that service operation. You can pass JSON text or a path to a JSON file.

## Safety flags

- Reads run without `--apply`.
- Leave out `--apply` for a preview. Use `--bind-aws --plan-out <path>` to save a plan tied to the AWS account and role.
- Live writes need `--apply --plan-in <path> --yes`.
- Add `--ack-no-snapshot` when the tool cannot save the previous state. The generated AWS writes require it.
- Use the same input when applying the plan.
- Add `--ack-spend-money` after approval for covered changes that can add charges.
- Add `--ack-irreversible` for delete-like or other hard-to-undo changes.
- Use `--receipt-out <path>` to save the live apply receipt.
- Use `--log-file <path>` if you want a second redacted audit log.
- Use `--output-file <path>` when the AWS response returns binary data.

## Shared flags

- `--env-file <path>` picks a local AWS settings file. The default is `.env`.
- `--timeout-s <seconds>` overrides the timeout for this command.
- `--config <path>`: optional project defaults JSON
- `--project-dir <path>`: project root for local config
- `--run-id <id>`: use a specific local run id
- `--artifacts-dir <path>`: write run proof somewhere else
- `--no-artifacts`: disable local run proof
- `--output text`: human-readable output instead of JSON

## How to find operations

Run `inventory summary` to check coverage. Use help for the service you need:

```bash
qwayk-aws-safe-agent-cli iam --help
qwayk-aws-safe-agent-cli ec2 --help
qwayk-aws-safe-agent-cli s3 --help
```

For the full coverage boundary, use [Check the pinned coverage boundary](api_coverage.md).
