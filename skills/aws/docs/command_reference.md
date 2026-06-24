# Command reference

This is the exact command list for the AWS tool. Start here after identity is clear and you already know which AWS service or operation you want to inspect or plan.

For the guided path, start with [What you can do with AWS](use_cases.md), [Set up AWS access locally](onboarding.md), and [Read the safety model](safety_model.md).

## Local commands

- `qwayk-aws-safe-agent-cli --output json --version`
- `qwayk-aws-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-aws-safe-agent-cli auth check`
- `qwayk-aws-safe-agent-cli inventory summary`
- `qwayk-aws-safe-agent-cli runs list [--limit 20]`
- `qwayk-aws-safe-agent-cli runs show --run-id <run-id>`

## AWS service commands

Each AWS service in the pinned inventory becomes a subcommand.

```bash
qwayk-aws-safe-agent-cli <service> <operation> [--input-json JSON_OR_PATH] [--output-file PATH]
```

Examples:

- `qwayk-aws-safe-agent-cli iam list-users`
- `qwayk-aws-safe-agent-cli ec2 describe-instances`
- `qwayk-aws-safe-agent-cli iam create-user --input-json '{"UserName":"demo"}'`

## Safety flags

- Reads run without `--apply`.
- Dry-run writes omit `--apply` and can use `--plan-out <path>`.
- Live writes need `--apply --plan-in <path> --yes`.
- Add `--ack-no-snapshot` when the write cannot capture a before-state. This is normally required for generated AWS writes.
- Add `--ack-irreversible` for delete-like or other hard-to-undo changes.
- Use `--receipt-out <path>` to save the live apply receipt. The receipt includes what verification checked and any read-back limit.
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
