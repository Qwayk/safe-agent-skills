# Authentication

Authentication means proving the tool is acting as the AWS identity you meant to use. AWS authentication is meant to be local: the tool uses the normal AWS credential chain through Boto3 and proves the active identity with STS before other service calls. Keep credentials on the machine, do not paste secrets into chat, and check the account and region before asking for any service read or planned change.

A good first auth check is: "Run the AWS auth check, tell me the account, ARN, user id, region, and whether the account and region allowlists passed."

## Required values

- `AWS_DEFAULT_REGION`: the region the first command should use.
- `AWS_PROFILE`: optional named local profile.
- `AWS_ALLOWED_ACCOUNTS`: optional comma-separated account allowlist.
- `AWS_ALLOWED_REGIONS`: optional comma-separated region allowlist.

The AWS access keys or SSO session are not stored in this repo. They come from the normal AWS setup on the machine.

## Safe check

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

The check calls STS `GetCallerIdentity`. The response shows the account, ARN, and user id that AWS sees, then the tool checks optional account and region allowlists.

## What success looks like

- `auth check` returns `ok: true`.
- The identity fields are present.
- The region is the one you expected.
- The allowlist result matches the account and region you wanted to use.

## What can fail

- `NoCredentialsError` usually means the machine does not have AWS credentials yet.
- An expired SSO session can make a profile fail even when the profile name is correct.
- A refusal about account or region usually means the allowlist protected the wrong target.
- A bad or missing profile usually means the AWS profile name is wrong or incomplete.
