# Troubleshooting

When AWS work fails, the useful clue is usually in the exact JSON error output: missing credentials, wrong profile, blocked account, blocked region, invalid input, binary output, or a refused write gate. A good first troubleshooting ask is: "Read the exact JSON error output, explain the safest next check, and stop before retrying anything that could change AWS."

Do not guess past an identity or allowlist error. Fix the local setup first, then run the smallest safe check again.

## Common issues

### No credentials

If `auth check` returns `NoCredentialsError`, the machine does not have AWS credentials yet or the selected profile is wrong.

Fix it by checking the local AWS profile, SSO login flow, shared config files, or environment-backed credentials.

### Wrong account or region

If the tool refuses because of `AWS_ALLOWED_ACCOUNTS` or `AWS_ALLOWED_REGIONS`, that is usually a good sign. It means the tool protected the wrong target.

Check the active profile, account id, and region before changing the allowlist.

### Bad input

If the tool says the input JSON is invalid or a parameter is missing, re-check the command syntax in [the command reference](command_reference.md). The CLI validates input against the pinned Botocore operation model before it runs.

### Write refusals

If a write refuses, check whether the command needs a reviewed plan, `--apply`, `--plan-in`, `--yes`, `--ack-no-snapshot`, or `--ack-irreversible`.

Do not add acknowledgement flags until the plan is reviewed and the account, region, service, operation, and input are correct.

### Binary output

Some AWS operations return binary data. If the tool refuses with a binary-output error, add `--output-file <path>` so binary data is not printed into chat or logs.

## More detail

- Use `--verbose` to see request start and end lines.
- Use `--debug` only when you need a Python stack trace.
- Secrets are redacted in normal output, logs, plans, and receipts.
