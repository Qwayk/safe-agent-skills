# Connect your AWS account

Set up the local AWS identity first, then ask for one safe read. You do not need to learn the command line first. The important part is knowing which account, role, and region the agent is about to touch.

Keep the setup files private. Put local values in `.env` or your normal AWS config files, keep them out of chat, and do not commit secrets to Git.

## What must already exist

The tool uses the normal AWS credential chain. That can mean an `AWS_PROFILE`, environment-backed credentials, SSO-backed credentials, or another local AWS setup already trusted on the machine.

You also need:

- `AWS_DEFAULT_REGION` for the region the first read should use
- optional `AWS_PROFILE` when you use a named local profile
- optional `AWS_ALLOWED_ACCOUNTS` when the tool should refuse every other account
- optional `AWS_ALLOWED_REGIONS` when the tool should refuse every other region

The first real AWS check is STS `GetCallerIdentity`. That check proves which identity is active before the agent touches any other AWS service.

## Step 1: Create the local setup file

Use the sample file if it is available in your private source folder, or create a local `.env` file with only the values you need.

```bash
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=your-profile-name
AWS_ALLOWED_ACCOUNTS=123456789012
AWS_ALLOWED_REGIONS=us-east-1
```

Use your real account and region values. Do not paste access keys, session tokens, or secret values into the chat.

## Step 2: Run the setup helper

```bash
qwayk-aws-safe-agent-cli onboarding
```

This shows what local setup is missing. If you want instructions only and do not want the helper to write a local env file, add `--no-write-env`.

## Step 3: Confirm the connection

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

A good result shows the AWS account, ARN, user id, selected region, and allowlist status. If the account or region is not the one you expected, stop and fix setup before running service commands.

## What to ask your AI agent (examples)

- "Check which AWS account and region this workspace is using, then stop."
- "Show the AWS inventory summary and tell me what kind of commands are available."
- "Run one read-only AWS check and explain which account and region it touched."
- "Prepare a dry-run plan for this change, but do not apply it."

## What success looks like

Setup is working when the agent can name the AWS identity, explain the region and allowlist result, run a harmless read, and tell you what would need a dry-run plan before any write.

If `auth check` fails on a clean machine, the usual cause is missing local AWS credentials, an expired SSO session, a wrong profile, or a missing region.
