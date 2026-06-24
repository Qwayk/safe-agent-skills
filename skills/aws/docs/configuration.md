# Configuration

Configuration means the local settings that tell the CLI which AWS profile, region, timeout, and guardrails to use. AWS configuration is the local set of values that controls those choices for each run. Put private values in `.env` or the `--env-file`, keep them out of chat and Git, and use allowlists when you want the tool to refuse the wrong AWS account or region before a live call.

A good first configuration check is: "Show me which AWS region, profile, account allowlist, and region allowlist this run will use before any service command."

## Files

- `.env`: local private values for this workspace
- `examples/example.env`: safe sample values
- optional JSON config file passed with `--config`

## Environment variables

| Variable | Meaning | Default |
| --- | --- | --- |
| `AWS_DEFAULT_REGION` | Region the tool should use for reads and writes | `us-east-1` |
| `AWS_PROFILE` | Named AWS profile to use from the local credential chain | blank |
| `AWS_ALLOWED_ACCOUNTS` | Comma-separated list of allowed AWS account ids | blank |
| `AWS_ALLOWED_REGIONS` | Comma-separated list of allowed regions | blank |
| `AWS_TIMEOUT_S` | Connect and read timeout in seconds | `30` |

## Precedence

- OS environment variables override `.env`.
- A value passed through the CLI can override local defaults where that flag exists.
- Boto3 still follows the normal AWS lookup order for credentials and region data.
- `AWS_ALLOWED_ACCOUNTS` and `AWS_ALLOWED_REGIONS` are guardrails, not secrets.

## What not to put here

- Access keys
- Secret keys
- Session tokens
- Any value you would not want written to a local text file
