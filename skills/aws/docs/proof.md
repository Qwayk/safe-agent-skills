# Proof and verification

This page is the evidence trail for the AWS skill. It shows what has actually been checked in code and tests, what was checked against the public copy, and what still needs a real AWS account before anyone should treat it as live-account proof.

If you only check one thing, check the latest local test result and the live-unverified notes before asking the agent to plan a change that could affect IAM, EC2, S3, billing, public access, secrets, data movement, or resource lifecycle.

No live AWS writes were run during local validation. The write path is covered by mocked apply checks, plan and receipt shapes, refusal checks, redaction checks, and local run history.

## What this proves

- the package installs and prints its version
- the pinned Boto3/Botocore 1.43.36 inventory is available locally
- the inventory maps 428 services and 18,727 generated named AWS operation commands
- the identity check reaches STS and shows the real error shape when no credentials are present
- a mutating AWS operation produces a dry-run plan before any live write
- a live write without a reviewed plan is refused before STS or AWS service calls
- a mocked live apply writes a receipt with verification fields and `limited` status when no read-back ran
- removed template commands are refused
- the example plan and receipt files match the AWS runtime shape
- committed generated inventory and example outputs do not leak local machine paths
- the coverage page links to a generated per-operation ledger with status and risk counts
- the AWS source and public mirror docs pass their AWS-specific contract tests

## What this does not prove

- It does not prove a real AWS account accepted any write.
- It does not prove every AWS operation has a useful operation-specific read-back.
- It does not prove your AWS role has permission for IAM, EC2, S3, CloudTrail, CloudWatch, billing, quotas, or any other service.
- It does not prove a `limited` receipt means the resource state changed correctly.

## Last verified

- Date (UTC): 2026-06-24
- Verified by: Codex
- Tool version: 0.1.0
- Boto3 version: 1.43.36
- Botocore version: 1.43.36

## Local verification

Run inside the tool folder:

1. Create venv and install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

2. Version check

```bash
qwayk-aws-safe-agent-cli --output json --version
```

3. Inventory summary

```bash
qwayk-aws-safe-agent-cli inventory summary
```

4. Identity check

```bash
qwayk-aws-safe-agent-cli --output json auth check
```

5. Dry-run write planning

```bash
qwayk-aws-safe-agent-cli --output json --no-artifacts iam create-user --input-json '{"UserName":"dry-run-user"}'
```

This returns `dry_run: true` and a plan for `iam create-user`. It does not call AWS.

6. Refused live apply without a reviewed plan

```bash
qwayk-aws-safe-agent-cli --output json ec2 terminate-instances --input-json '{"InstanceIds":["i-1234567890abcdef0"]}' --apply
```

This returns a refusal before any AWS service call because `--plan-in`, `--yes`, and the extra acknowledgement flags are missing.

7. Local tests

```bash
.venv/bin/python -m unittest -q
```

The final quality-loop check on 2026-06-24 passed 45 unit tests. Those tests cover dry-run writes, refused apply without a plan, mocked apply with a plan, verification receipt fields, stronger risk categories, generated coverage counts, and committed-proof path hygiene.

The repo-wide new-tool flow audit is not listed here as AWS proof because the current worktree has an unrelated GCP template-guide blocker outside this AWS skill.

## Example outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/inventory_summary.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong

- `NoCredentialsError` means the machine does not have AWS credentials yet.
- An allowlist refusal means the tool blocked the wrong account or region.
- A write refusal without `--plan-in`, `--apply`, or `--yes` means the safety gates are working.
- A write refusal asking for `--ack-no-snapshot` means the generated AWS path has no generic safe before-state or read-back for that operation.
- A receipt with `verification.status: limited` means the SDK call returned and the plan was checked, but no operation-specific resource read-back ran. A 2xx response alone does not make the receipt `verified`.
- A binary output refusal means `--output-file` is required.
- Refusal of removed starter-template commands means the starter template surface is gone.

## Honest limits

- These checks prove local behavior, generated coverage, and mocked apply safety. They do not prove that a real AWS account accepted or rejected every operation.
- AWS eventual consistency can delay visible state after a successful write.
- Some AWS operations have side effects that cannot be undone automatically. The tool slows those down with plan review and acknowledgement flags, but it does not make them risk-free.

## Links

- [Official and local references](references.md)
- [Pinned coverage boundary](api_coverage.md)
