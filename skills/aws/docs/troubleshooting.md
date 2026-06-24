# Troubleshooting

Start with the exact JSON error output. AWS failures are usually one of five things: no credentials, wrong profile, wrong region, missing permission, or a safety gate that correctly stopped a risky command.

A good first troubleshooting ask is: "Read this AWS JSON error output, explain the likely cause, and give me the safest next check without inventing missing data."

Before retrying anything that could change access, spend, public exposure, data movement, messages, secrets, or resources, confirm the account, role, region, and target resource again.

## Common issues

## No credentials

If `auth check` returns `NoCredentialsError`, the machine does not have AWS credentials yet or the selected profile is wrong.

Check the local AWS profile, SSO login, role session, or shared config files. Nothing changed in AWS when the identity check fails this early.

## Wrong account or region

If the tool refuses because of `AWS_ALLOWED_ACCOUNTS` or `AWS_ALLOWED_REGIONS`, treat that as a useful stop. It means the configured guardrail protected the wrong AWS target.

Fix the profile, region, or allowlist before trying again.

## Permissions

If AWS returns an access-denied style error, the caller may be correct but under-permissioned for that service. Decide whether the requested read or change should be allowed before expanding permissions.

Do not give broader AWS permissions just to make a command pass.

For a read-only review, choose another safe read if the blocked service is not essential. For a real change, stop until the right person confirms the permission should exist.

## Bad input

If the tool says the input JSON is invalid or a parameter is missing, re-check the operation syntax in [the command reference](command_reference.md).

The CLI validates input against the pinned Botocore model for that operation.

## Write refusals

A write refusal usually means one of these is missing:

- a dry-run plan
- `--plan-in`
- `--apply`
- `--yes`
- `--ack-no-snapshot`
- `--ack-irreversible`

Read the plan first. The missing flag is not just a command detail; it marks a real AWS risk that needs review.

## Limited verification

A receipt with `verification.status: limited` means the reviewed plan matched and the SDK response was captured, but the tool did not run an operation-specific read-back.

For important infrastructure, identity, public access, or spend changes, run a separate read after apply to inspect the resulting resource state.

For example, after a security group change, read the security group again. After an IAM user or policy change, read the IAM target again. After a bucket policy change, read the bucket policy and public-access settings again.

## Binary output

Some AWS operations return binary data. If the tool refuses with a binary-output error, add `--output-file <path>` so the payload is saved to a file instead of printed.

## Debug errors

- Use `--verbose` to see request start and end lines.
- Use `--debug` only when you need a Python stack trace.
- Secrets are redacted in normal output, logs, plans, and receipts.
