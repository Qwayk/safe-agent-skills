# Connect your AWS account

You do not need to learn every AWS command first. Once setup is done, your agent can prove the caller, check the region, inspect AWS resources, and stop before risky changes.

Keep the setup files private. Do not paste AWS access keys, secret keys, session tokens, local profile files, or `.env` values into chat.

## Before you start

- You need a local AWS profile, SSO login, role, or credential setup that already works on this machine.
- The local `.env` file is just the private settings file for this tool.
- Account and region allowlists are optional guardrails that help prevent work in the wrong AWS target.

## Step 1: choose the AWS identity

Decide which local AWS profile or role the tool should use. If you use named profiles, choose the profile that already has the right permissions for the account you want to inspect.

The tool follows the normal AWS credential chain through Boto3. It does not need secret values in chat.

## Step 2: add local settings

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Keep `.env` private.
3. Set `AWS_DEFAULT_REGION`.
4. Add `AWS_PROFILE` if you use a named profile.
5. Add `AWS_ALLOWED_ACCOUNTS` when the tool should refuse every other AWS account.
6. Add `AWS_ALLOWED_REGIONS` when the tool should refuse every other region.

If your host needs a visible sample, use `examples/example.env` as the placeholder guide.

## Step 3: run the setup helper

```bash
qwayk-aws-safe-agent-cli onboarding
```

Add `--no-write-env` if you only want instructions and do not want the helper to create `.env`.

## Step 4: confirm the connection

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

A good result shows the AWS account, ARN, user id, region, and allowlist status.

## What success looks like

Setup is complete when `auth check` succeeds and your agent can name the AWS identity, confirm the region, explain whether allowlists passed, and suggest one safe read without changing anything.

If `auth check` fails on a clean machine, the usual causes are missing credentials, an expired login, a wrong profile name, a missing region, or an allowlist that correctly blocked the target.

## What to ask your AI agent (examples)

- "Check which AWS account and region this workspace is using, then stop."
- "Show me what AWS resources you can review safely before any write."
- "List IAM users and access keys we should review first."
- "Check EC2 instances in this region and point out likely cost risk."
- "Review S3 bucket settings before any policy change."
- "Prepare a dry-run plan for this AWS change, but do not apply it."
