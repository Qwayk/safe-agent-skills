# Configuration

Configuration means the local settings that tell the CLI which AWS profile, region, timeout, and guardrails to use.

AWS configuration is the local choice of profile, region, timeout, and account or region allowlists. Put private values in `.env` or the `--env-file` path, keep them out of chat and Git, and use allowlists when the wrong AWS account or region would be risky.

A good first configuration check is: confirm `AWS_DEFAULT_REGION`, `AWS_PROFILE`, `AWS_ALLOWED_ACCOUNTS`, and `AWS_ALLOWED_REGIONS` before running `auth check` or planning a write.

## Files

- Create `.env` locally and keep it private.

## Environment variables

| Variable | Meaning | Default |
| --- | --- | --- |
| `AWS_DEFAULT_REGION` | Region the tool should use for reads and writes | `us-east-1` |
| `AWS_PROFILE` | Named AWS profile to use from the local credential chain | blank |
| `AWS_ALLOWED_ACCOUNTS` | Comma-separated list of allowed AWS account ids | blank |
| `AWS_ALLOWED_REGIONS` | Comma-separated list of allowed regions | blank |
| `AWS_TIMEOUT_S` | Connect and read timeout in seconds | `30` |

## How the settings work

- OS environment variables override `.env`.
- Boto3 supplies the normal AWS lookup order for credentials and region data.
- `AWS_ALLOWED_ACCOUNTS` and `AWS_ALLOWED_REGIONS` are guardrails, not secrets.
- Allowlist values should be narrow for production or client accounts.
- If a machine can reach several AWS accounts, set allowlists before asking for any live write plan.

## Good configuration examples

- Local sandbox review: set the sandbox profile and one sandbox region.
- Production read review: set the production read-only profile, production account id, and the one region you intend to inspect first.
- Client account work: set the client account id in `AWS_ALLOWED_ACCOUNTS` so a wrong profile stops before service calls.
- Multi-region review: start with one region, then repeat intentionally for each additional region instead of letting the agent wander.

## What not to put here

- AWS access keys
- AWS secret keys
- AWS session tokens
- Customer secrets or passwords
- Any value you would not want saved in a local text file
