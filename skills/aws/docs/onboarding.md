# Connect your AWS account

Connect the AWS account the same careful way you would start a cloud review: choose the local profile or role, confirm the region, prove who AWS thinks you are, then run a small read before any change.

Keep the setup files private. Do not paste AWS access keys, secret keys, session tokens, local profile files, or `.env` values into chat.

## Before you start

- You need a local AWS profile, SSO login, assumed role, or credential setup that already works on this machine.
- You need to know which region you want the first check to use.
- If this machine can reach more than one AWS account, use allowlists before planning any write.
- The local `.env` file is only for this tool's private settings. It is not for chat and it is not for Git.

## Step 1: choose the AWS identity

Decide which local AWS profile or role the tool should use. If you use named profiles, choose the profile that already has the right permissions for the account you want to inspect.

The tool follows the normal AWS credential chain through Boto3. It does not need secret values in chat.

Good choices:

- a read-only or audit role for first review work
- a named profile that points at the intended account
- a short-lived SSO or assumed-role session when your team uses AWS SSO

Avoid starting from a broad admin profile unless you truly need it for the job.

## Step 2: add local settings

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Keep `.env` private.
3. Set `AWS_DEFAULT_REGION`.
4. Add `AWS_PROFILE` if you use a named profile.
5. Add `AWS_ALLOWED_ACCOUNTS` when the tool should refuse every other AWS account.
6. Add `AWS_ALLOWED_REGIONS` when the tool should refuse every other region.

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

After setup, a good first review is IAM users, EC2 instances, or S3 buckets. If those are not allowed, ask the agent to explain which permission is missing and choose another safe read.

## What to ask your AI agent (examples)

- "Check which AWS account and region this workspace is using, then stop."
- "Show me what AWS resources you can review safely before any write."
- "List IAM users and access keys we should review first."
- "Check EC2 instances in this region and point out likely cost risk."
- "Review S3 bucket settings before any policy change."
- "Prepare a dry-run plan for this AWS change, but do not apply it."
