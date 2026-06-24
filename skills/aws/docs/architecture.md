# Architecture

Read this page when you want to check how the AWS skill is built. Normal users should start with the quickstart and use cases; this page is for people reviewing the code path behind the promises.

The AWS skill is built as a small command-line tool around Boto3, the official AWS Python SDK. It loads a pinned Botocore model inventory, turns AWS operations into named commands, checks identity with STS, validates input, classifies risk, creates dry-run plans for writes, and saves redacted receipts after live attempts. This matters when an agent is using the skill for real work.

A good architecture check is: trace one command from `cli.py` into `aws_runtime.py`, confirm STS identity and allowlists run before AWS service calls, and verify that write commands produce plans and receipts.

## Runtime

- `cli.py`: the entrypoint that calls the AWS runtime.
- `aws_runtime.py`: argument parsing, generated service commands, risk classification, dry-run plans, live apply gates, receipt verification, and output handling.
- `generated_registry.py`: reads `docs/_generated/aws_botocore_inventory.json` and turns the pinned inventory into service and operation lookups.
- `model_loader.py`: loads operation models from the pinned Botocore package for input validation.
- `validation.py`: checks `--input-json` against the Botocore operation model before a command runs.
- `commands/auth.py`, `commands/inventory.py`, and `commands/onboarding.py`: the small local command handlers.
- `sts_identity.py` and `allowlists.py`: prove the AWS caller and block the wrong account or region.
- `runs.py`: local run folders and the `.state/runs/index.jsonl` history file.
- `audit_log.py`, `redaction.py`, and `output.py`: redacted events and the one-JSON-object stdout contract.
- `json_files.py`: safe JSON helpers for plan and receipt files.

## Generated inventory

The coverage boundary comes from the packaged Botocore data in the pinned Boto3/Botocore wheel. The generator writes two files together:

- `docs/_generated/aws_botocore_inventory.json`
- `docs/api_coverage.md`

If the pinned SDK version changes, regenerate both files and rerun the full AWS test suite.

The runtime does not load service models from `~/.aws/models` or `AWS_DATA_PATH`. That keeps the coverage claim tied to the package that was tested and mirrored.

## Runtime flow

1. Load `.env` and project settings.
2. Load the generated registry and the Botocore operation model.
3. Check the AWS identity with STS before non-STS service calls.
4. Validate the input JSON against the pinned operation model.
5. Classify the operation as read, write, no-snapshot, unknown mutating, irreversible, or another documented risk category.
6. For reads, call the named Boto3 client operation.
7. For writes, create a dry-run plan first. Live apply requires a reviewed plan, `--apply`, and `--yes`; higher-risk writes require the extra acknowledgement flags.
8. Save redacted run proof under `.state/runs/` unless the caller disables artifacts.

## Verification boundary

Generic generated AWS writes cannot always infer the correct safe read-back operation. When no operation-specific read-back exists, the receipt says verification is `limited` and records the SDK response and plan checks instead of claiming full resource verification.
