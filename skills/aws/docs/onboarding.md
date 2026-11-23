# Set up AWS access

Choose the AWS account, role and region you want to inspect, then run one small read you can check. Use a role that already has permission to read that resource.

## Connect your AWS account

The tool uses the sign-in that Boto3 finds on your machine. You can use a named AWS profile, AWS IAM Identity Center (single sign-on), or an AWS role. If your team uses single sign-on, sign in locally before running the tool. Keep access keys, secret keys, session tokens and AWS profile files on your machine. [AWS sign-in options](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html)

## Choose a settings file

The setup helper can create a private file for optional settings. It keeps an existing file and shows the next command with the path you chose. Add `--no-write-env` to see the instructions without creating a file.

```bash
qwayk-aws-safe-agent-cli onboarding
qwayk-aws-safe-agent-cli --env-file "aws settings.env" onboarding
```

| Setting | What it does |
| --- | --- |
| `AWS_PROFILE` | Picks a named AWS profile. Leave it blank to use the usual AWS sign-in on this machine. |
| `AWS_DEFAULT_REGION` | Overrides the profile’s region. If both are blank, the tool uses `us-east-1`. |
| `AWS_ALLOWED_ACCOUNTS` | Limits the tool to these AWS account IDs when set. |
| `AWS_ALLOWED_REGIONS` | Limits the tool to these AWS regions when set. |
| `AWS_TIMEOUT_S` | Sets the connection and response timeout in seconds. The default is 30. |

Use commas between entries in the account and region lists. Environment variables take priority over values in the settings file. Keep private settings and `.state/runs/` out of Git and chat.

## Confirm the account, role and region

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

AWS STS reports the account and ARN, which identifies the signed-in user or role. Check that account, the region and the `auth.allowlists.allowed` field. Then [run one small read](quickstart.md) to confirm that the role can use the service you picked. The identity check can succeed even if the role lacks service permissions. [AWS identity check](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)

## Fix a problem

| What you see | What to check |
| --- | --- |
| Missing credentials, expired session or profile error | Check the profile name and sign in again if needed. |
| Wrong account or region | Compare the sign-in and the selected region with the expected target. If a configured list blocked the call, confirm the target before changing the list. |
| Access denied on a read | Check whether that role has permission for the exact service and resource. Use another small read if it would answer the same question. |
| Invalid JSON or missing fields | Check the command’s input fields in [the command guide](command_reference.md). |
| The command needs an output file | Set `--output-file` to a private location for the binary result. |
| An apply flag or receipt status is unclear | Use [the review and receipt steps](safety_model.md). |

Start with the exact error. Use `--debug` only when you need the Python stack trace. Keep private values out of anything you share.
