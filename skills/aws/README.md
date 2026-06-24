# AWS Safe Agent CLI

AWS is where one small mistake can touch real servers, access keys, storage buckets, customer data, or spend. This skill gives your agent a safer way to work there: prove the account and region first, inspect what matters, then stop for a reviewed plan before any live change.

It is useful for practical AWS checks such as IAM access reviews, EC2 instance inventory, S3 exposure checks, billing and quota review, CloudWatch or CloudTrail lookups, and cautious change planning across the pinned AWS service models.

A good first ask is: `Check my AWS identity and region, then show the safest AWS review to run before any change.`

## Start here first

- [See real AWS jobs this skill helps with](docs/use_cases.md)
- [Set up AWS access locally](docs/onboarding.md)
- [Understand the AWS safety rules](docs/safety_model.md)
- [Run the first safe AWS checks](docs/quickstart.md)
- [Use the exact command guide](docs/command_reference.md)

If you already know the job, go to [Install and first run](#install-and-first-run). If you want evidence before trusting it, go to [Helpful docs](#helpful-docs).

## What this skill helps with

- Confirm the AWS account, caller ARN, and region before touching another service.
- Review IAM users, roles, policies, access keys, and other identity-sensitive resources.
- Inspect common infrastructure areas such as EC2, S3, Lambda, RDS, CloudWatch, CloudTrail, Route 53, billing, quotas, and messaging services.
- Flag whether a requested change may affect identity, secrets, public exposure, spend, data movement, messaging, or hard-to-undo resources.
- Turn AWS writes into dry-run plans so a person or reviewer can inspect the exact service, operation, region, and input before apply.
- Keep redacted local proof after write attempts so the next person can see what was planned, what ran, and what verification could or could not prove.

## Example requests

- Check which AWS account, role, and region this workspace is using, then stop.
- Show IAM users and access keys so we can decide what needs a human access review.
- List EC2 instances in this region and point out anything that could cost money if left running.
- Review S3 bucket access settings and tell me which buckets deserve a public-access check.
- Check CloudTrail or CloudWatch for the safest recent evidence before we change a resource.
- Show service quota or billing-related information that helps explain a spend risk.
- Prepare a dry-run plan to create a limited IAM user named `reporting-bot`, but do not apply it.
- Prepare a plan to stop one EC2 instance and explain the approval flags it would need.
- Tell me whether this AWS request touches identity, secrets, spend, public exposure, messaging, data movement, or an irreversible action.

## What access this skill needs

- Local AWS credentials from the normal AWS credential chain, or an `AWS_PROFILE` that points to the intended role.
- A region in `AWS_DEFAULT_REGION`.
- Optional account and region allowlists in `AWS_ALLOWED_ACCOUNTS` and `AWS_ALLOWED_REGIONS` so the tool refuses the wrong target.
- Permission to call STS `GetCallerIdentity`; this is the first identity check.
- Permission for the specific AWS read or change you ask for.
- No AWS access keys, secret keys, or session tokens pasted into chat.

## Install and first run

Install slug: `aws`

Ask your agent to install the skill from `Qwayk/safe-agent-skills`.

If auto-install is not available, run:

```bash
npx skills add Qwayk/safe-agent-skills@aws -g -y
```

Then:

1. Run `qwayk-aws-safe-agent-cli --output json --version`.
2. Run `qwayk-aws-safe-agent-cli onboarding`.
3. Run `qwayk-aws-safe-agent-cli --output json auth check`.
4. Ask for one read-only AWS review, such as IAM users, EC2 instances, S3 bucket settings, or the pinned inventory summary.

## How this skill stays safe

- It checks STS identity before non-STS AWS service calls.
- It can refuse a call when the account or region is outside your allowlists.
- Reads can run without apply flags.
- Writes start as dry-run plans.
- Live writes need a reviewed `--plan-in` file, `--apply`, and `--yes`.
- Generated AWS writes usually need `--ack-no-snapshot` because the generic Botocore model path cannot save a reliable before-state or infer a safe read-back for every operation.
- Delete-like or otherwise hard-to-undo operations need `--ack-irreversible`.
- Plans, receipts, logs, and run-history files are redacted.
- Binary or sensitive payloads must go to a file instead of being printed to stdout.

## What it covers today

- `onboarding`
- `auth check`
- `inventory summary`
- `runs list`
- `runs show`
- 428 pinned Botocore services from Boto3/Botocore 1.43.36
- 18,727 generated named AWS operation commands from the packaged Botocore service models
- Read operations, dry-run write plans, and reviewed live writes for those named operations

## What happens before live changes

- The tool builds a dry-run plan first.
- The plan names the AWS service, operation, region, profile, allowlists, risk categories, and input.
- The apply path refuses if the current service, operation, region, or input no longer matches the reviewed plan.
- `--plan-in`, `--apply`, and `--yes` are required for live writes.
- `--ack-no-snapshot` is required when no useful before-state or generic read-back is available. For generated AWS writes, this is the normal case today.
- `--ack-irreversible` is required for delete-like or other hard-to-undo actions.
- `--output-file` is required when an AWS operation returns binary data.

## What proof it leaves behind

- `plan.json` in the local run folder for dry-run writes.
- `receipt.json` after live apply, including verification checks and any read-back limit.
- `summary.md` with a plain record of the run.
- `audit.jsonl` with redacted events.
- `.state/runs/index.jsonl` for local run history.
- Redacted examples in `docs/examples/`.

## Limits

- AWS live account behavior remains live-unverified unless you run the tool with real AWS credentials.
- Local validation did not run live AWS writes. Tests cover mocked apply, refusal behavior, plan and receipt shape, redaction, and coverage.
- Generic generated AWS writes do not currently save operation-specific before-state. Receipts say `limited` when verification only proves that the reviewed plan matched and the AWS SDK returned a captured response.
- The coverage boundary is the pinned Boto3/Botocore 1.43.36 package shipped with this tool. It does not load extra service models from `~/.aws/models` or `AWS_DATA_PATH`.
- The CLI exposes named commands generated from the pinned models. It is not a raw AWS call-anything bridge.

## Helpful docs

- [Browse the AWS docs hub](docs/README.md)
- [Run the first safe AWS checks](docs/quickstart.md)
- [Use the command guide](docs/command_reference.md)
- [Understand safety and approvals](docs/safety_model.md)
- [Check the pinned coverage boundary](docs/api_coverage.md)
- [Review proof and examples](docs/proof.md)
- [Set up AWS authentication](docs/authentication.md)
- [Choose useful AWS tasks](docs/use_cases.md)
