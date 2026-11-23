# AWS

Check what’s running in an AWS account, who can access it, and what may be adding to your bill. Start with the account, role and region you recognize. The agent checks that connection and runs a small read before suggesting a change.

> Check which AWS account, role and region you’re using. List the EC2 instances in that region and tell me what’s running. Wait before changing anything.

## What you can ask for

- Review IAM users, roles and policies for access that needs a closer look.
- See whether S3 buckets or network settings could expose data.
- Check EC2, RDS and other running resources for costs worth reviewing.
- Look at CloudTrail events or CloudWatch alarms after a problem.
- Prepare a plan for an AWS change and show what needs approval.

[More AWS examples](docs/use_cases.md) · [Commands and input files](docs/command_reference.md)

## Before a change

A write first shows a preview. Use `--bind-aws` to save a plan for the actual AWS account and role. The tool checks that the account, role, region, endpoint and request still match when you apply the plan. Some changes, such as starting an EC2 instance, also need explicit permission to spend money. The receipt shows what AWS reported and what you still need to check. [Review and approval steps](docs/safety_model.md)

## Install

Ask your agent to install `aws` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@aws -g -y
```

If you already have the CLI files, install with Python 3.12 or later from the tool folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Connect with a local AWS profile, single sign-on or a role. Keep access keys and session tokens on your machine. [Set up access](docs/onboarding.md) · [Run a first read](docs/quickstart.md)

## Coverage and checks

The inventory lists 428 services and 18,727 operations from Boto3 and Botocore 1.43.36. The CLI can call 18,722 of them when AWS permissions allow. Five need two-way streaming that this SDK cannot run. The install and safety checks have been tested with simulated AWS replies. A real AWS account check is separate. [API coverage](docs/api_coverage.md) · [Test results](docs/proof.md) · [All guides](docs/README.md)
