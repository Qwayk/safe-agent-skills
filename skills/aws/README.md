# AWS Safe Agent CLI

AWS controls infrastructure, access, data, and spend. This skill helps an agent work in AWS without guessing which account it is touching or jumping straight to a live change.

It starts by proving the AWS identity and region, then lets the agent inspect resources or prepare a reviewed plan for changes across IAM, EC2, S3, billing, messaging, and other AWS services.

A good first ask is: `Check my AWS identity and show the safest first thing to review.`

## Start here first

- [See the real jobs this tool helps with](docs/use_cases.md)
- [Set up AWS access locally](docs/onboarding.md)
- [Read the safety rules first](docs/safety_model.md)
- [Run the first safe checks](docs/quickstart.md)
- [See the command list](docs/command_reference.md)

If you already know what you want to run, jump straight to [Install and first run](#install-and-first-run) or [Helpful docs](#helpful-docs).

## What this skill helps with

- Check which AWS account, role, and region the tool is actually using.
- Review AWS services and resources before asking for a change.
- Prepare dry-run plans for writes and keep them out of live AWS until they are reviewed.
- Save redacted proof so the next person can see what was checked and what changed.

## Example requests

- Check which AWS account and region this workspace is using, then stop.
- List IAM users and tell me which ones look safest to review first.
- Show EC2 instances in this region and flag anything that looks risky to stop.
- Review S3 bucket access settings before I ask for any policy change.
- Prepare a dry-run plan to create a new IAM user named `reporting-bot`, but do not apply it.
- Prepare a plan to stop one EC2 instance and explain why the change needs extra approval.
- Tell me whether this AWS change touches spend, public access, secrets, or identity.

## What access this skill needs

- Access to the AWS credential chain on the machine, or an `AWS_PROFILE` that can assume the right role.
- A default region in `AWS_DEFAULT_REGION`.
- Optional allowlists in `AWS_ALLOWED_ACCOUNTS` and `AWS_ALLOWED_REGIONS` when you want the tool to refuse the wrong account or region.
- Permission to call STS `GetCallerIdentity` for the first identity check.
- Permission for the AWS actions you actually want the tool to read or change.
- No secret values pasted into chat.

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
3. Run `qwayk-aws-safe-agent-cli auth check`.
4. Ask for one read-only AWS service command after the identity check passes.

## How this skill stays safe

- Reads run without `--apply`.
- Writes start as dry-run plans.
- Live writes need a reviewed `--plan-in` file, `--apply`, and `--yes`.
- Generic AWS writes are treated as no-snapshot unless a later operation-specific read-back is added, so live writes normally need `--ack-no-snapshot`.
- Irreversible writes need `--ack-irreversible`.
- The tool checks STS identity and allowlists before non-STS service calls.
- Plans, receipts, logs, and `.state/runs/` artifacts are redacted.
- Binary output goes to a file instead of stdout.

## What it covers today

- `onboarding`
- `auth check`
- `inventory summary`
- `runs list`
- `runs show`
- Pinned Botocore service commands for every shipped AWS service model in the inventory.
- Read operations, dry-run write plans, and reviewed live writes for named AWS operations.

## What happens before live changes

- The tool builds a dry-run plan first.
- The plan names the AWS service, operation, region, profile, allowlists, risk, and input.
- The live apply path refuses if the service, operation, region, or input no longer matches the reviewed plan.
- `--plan-in` and `--yes` are required for live writes.
- `--ack-no-snapshot` is required when the write cannot save a before-state. In the generated AWS surface, this is the normal case.
- `--ack-irreversible` is required for delete-like or other hard-to-undo actions.
- If the command returns binary data, `--output-file` is required before the call can proceed.

## What proof it leaves behind

- `plan.json` in the run folder for dry-run writes.
- `receipt.json` after a live apply, including the verification checks that ran and any read-back limit.
- `summary.md` with a plain record of the run.
- `audit.jsonl` with redacted events.
- `.state/runs/index.jsonl` for local history.
- Sample outputs in `docs/examples/outputs/`.

## Limits

- The tool uses the pinned Botocore inventory that ships with the package. It does not read `~/.aws/models` or `AWS_DATA_PATH`.
- It only exposes named AWS commands generated from the pinned model.
- Local validation did not run live AWS writes. Receipts clearly say when verification is limited to the reviewed plan and AWS SDK response.
- Some AWS responses need `--output-file` because they return binary data.

## Helpful docs

- [Start with the user path](docs/README.md)
- [Run the first safe checks](docs/quickstart.md)
- [See the command list](docs/command_reference.md)
- [Read the safety model](docs/safety_model.md)
- [Check the coverage boundary](docs/api_coverage.md)
- [Check proof and examples](docs/proof.md)
- [See AWS setup notes](docs/onboarding.md)
- [Look at real use cases](docs/use_cases.md)
