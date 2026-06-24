# Quickstart

The first useful result is to confirm which AWS identity the tool is actually using. After that, run one harmless read that does not change the account. AWS can touch access, public exposure, data, and spend, so the first run should prove the account, region, and safety path before any change is planned.

A good first ask is: "Check which AWS account and region this skill is using, show the local AWS inventory summary, then stop before any change."

## What you will do first

You will do four things:

1. Confirm the CLI runs.
2. Confirm AWS identity with STS.
3. Run one small read.
4. Stop before anything that could change infrastructure, access, billing, data, messaging, or public exposure.

Before you begin, make sure AWS credentials are already available on the machine through the normal AWS credential chain or a named `AWS_PROFILE`. Keep secrets out of chat. If setup is not ready yet, use [Set up AWS access locally](onboarding.md).

## 1. Check the tool version

```bash
qwayk-aws-safe-agent-cli --output json --version
```

The result should show the CLI version plus the pinned `boto3` and `botocore` versions. This proves the installed command is the AWS skill command, not a different local script.

## 2. Check the AWS identity

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

A useful result names the AWS account, ARN, user id, region, and allowlist status. If this fails, stop and fix credentials or region setup before asking for service data. Do not work around an identity failure by trying random service commands.

## 3. Run one small first read

```bash
qwayk-aws-safe-agent-cli inventory summary
```

This reads the pinned AWS command inventory that ships with the skill. It is a safe first check because it does not touch live AWS resources, does not need write approval, and shows the size of the AWS surface the tool can name.

After that, choose one small service read that matches the job. Good first examples are listing IAM users, describing EC2 instances in one region, or reviewing S3 bucket settings. Ask the agent to explain which account and region the read will touch before it runs.

## 4. Stop before anything risky

Do not ask for live writes in the first quickstart run. For AWS, risky work includes anything that can change identity, permissions, public access, network exposure, compute state, data movement, messaging, secrets, quotas, or spend.

If you need a change, ask for a dry-run plan first. A live write needs a reviewed plan file, `--apply`, `--plan-in`, and `--yes`. Many generated AWS writes also need `--ack-no-snapshot`, and delete-like changes may need `--ack-irreversible`.

## What a useful first result includes

The first result should tell you:

- which AWS account and role were used
- which region was used
- whether account or region allowlists passed
- what was read
- whether anything was refused
- the safest next read or planning step

If the agent cannot say those things clearly, stop and ask it to run `auth check` again before doing more.

## Where to go next

- [What the tool helps you do](use_cases.md) for practical jobs
- [How this stays safe](safety_model.md) before any planned change
- [Command reference](command_reference.md) for exact command shape
- [Proof and verification](proof.md) for what has been tested
