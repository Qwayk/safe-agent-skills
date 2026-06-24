# Proof and verification

Most users do not need to run these checks every day. This page answers what has actually been checked for the AWS skill: install behavior, pinned inventory, dry-run planning, refused unsafe applies, receipt shape, and local proof files. It also says what was not proved live, so a 2xx AWS SDK response is not mistaken for full verification.

If you only check one thing, read the "Last verified" section and confirm the 45-test run plus the public copy audit were run for the same AWS version you are using.

No live AWS writes were run during local validation. The write path is covered by mocked apply checks, plan and receipt shapes, refusal checks, and local run history.

## What this page proves

- the tool installs and prints its version
- the pinned AWS inventory is available locally
- the identity check reaches STS and shows the real error shape when no credentials are present
- a mutating AWS operation produces a dry-run plan before any live write
- a live write without a reviewed plan is refused before STS or AWS service calls
- a mocked live apply writes a receipt with verification fields and `limited` status when no read-back ran
- removed template commands are refused
- the example plan and receipt files match the AWS runtime shape
- committed generated inventory and example outputs do not leak local machine paths
- the coverage page links to a generated per-operation ledger with status and risk counts
- the source docs pass the repo's new-tool audit

## Last verified

- Date (UTC): 2026-06-24
- Verified by: Codex
- Tool version: 0.1.0
- boto3 version: 1.43.36
- botocore version: 1.43.36

## Smoke checks

Run inside the tool folder:

1. Create venv + install

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

7. Local tests and audits

```bash
.venv/bin/python -m unittest -q
```

The final source check on 2026-06-24 passed the repo new-tool audit and 45 unit tests. Those tests cover dry-run writes, refused apply without a plan, mocked apply with a plan, verification receipt fields, stronger risk categories, generated coverage counts, and committed-proof path hygiene.

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

## Links

- [References](references.md)
- [API coverage](api_coverage.md)
