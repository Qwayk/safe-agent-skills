# AWS test results

## November 23, 2026 local checks

The source and local catalog copies each passed 36 tests after a fresh Python install outside the repo. Both packages loaded 428 services. I matched the 18,727 operations in the inventory to Boto3 and Botocore 1.43.36. The SDK exposes methods for 18,722. The other five need two-way event streams, which Boto3 cannot run. The CLI explains that before contacting AWS. The generator reproduced the packaged inventory and coverage guide. [Coverage and SDK limits](api_coverage.md)

The tests checked that setup keeps the selected settings file and uses the profile’s region unless an explicit region is set. Simulated replies covered changes to the account, role, endpoint, region, and inputs, including secrets hidden in the saved plan. They also covered spending approval, a pending EC2 start, and a lost reply. None of these checks called AWS.

## June 24, 2026 source checks

Codex recorded 45 passing tests for version `0.1.0` with Boto3 and Botocore 1.43.36. They covered offline previews, refusal before a write without approval, simulated apply replies and limited verification, local run history, coverage counts and portable examples. The setup check reported `NoCredentialsError` on a clean machine. The public copy also passed the AWS guide tests at the time. A GCP template-guide finding prevented using the repo-wide audit as AWS proof on that date.

## Repeat the local checks

From the tool folder, use Python 3.12 or later:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-aws-safe-agent-cli --output json --version
.venv/bin/qwayk-aws-safe-agent-cli inventory summary
.venv/bin/python -m unittest -q
```

An offline preview needs no AWS sign-in:

```bash
qwayk-aws-safe-agent-cli --output json --no-artifacts iam create-user --input-json '{"UserName":"dry-run-user"}'
```

The following command refuses before contacting AWS because the approval flags and plan are missing:

```bash
qwayk-aws-safe-agent-cli --output json ec2 terminate-instances --input-json '{"InstanceIds":["i-1234567890abcdef0"]}' --apply
```

## What still needs a real account

Run `qwayk-aws-safe-agent-cli --output json auth check` with the intended role. [Read one resource you recognize](quickstart.md) to confirm that role’s access. A write needs its own [plan and approval](safety_model.md). A successful SDK reply stays limited verification until you read the affected resource.

## Saved examples

The [examples](examples/) show the version, the June inventory and the identity check output. The saved plan and receipt show the older formats. Generate a fresh plan with `--bind-aws` for the current workflow. [Official sources](references.md)
