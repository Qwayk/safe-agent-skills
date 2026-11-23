# Architecture

The CLI uses Boto3, the AWS Python SDK, to run named operations from the packaged Botocore model list. One runtime checks input, looks up the AWS account and role, and saves plans and receipts.

## Runtime

- `cli.py`: the entrypoint that calls the AWS runtime.
- `aws_runtime.py`: argument parsing, generated service commands, risk classification, dry-run plans, live apply gates, receipt verification, and output handling.
- `generated_registry.py`: reads `src/aws_safe_agent_cli/aws_botocore_inventory.json` and turns the pinned inventory into service and operation lookups.
- `model_loader.py`: loads operation models from the pinned Botocore package for input validation.
- `validation.py`: checks `--input-json` against the Botocore operation model before a command runs.
- `commands/auth.py`, `commands/inventory.py`, and `commands/onboarding.py`: the small local command handlers.
- `sts_identity.py` and `allowlists.py`: prove the AWS caller and block the wrong account or region.
- `runs.py`: local run folders and the `.state/runs/index.jsonl` history file.
- `audit_log.py`, `redaction.py`, and `output.py`: redacted events and the one-JSON-object stdout contract.
- `json_files.py`: safe JSON helpers for plan and receipt files.

## Generated inventory

The coverage boundary comes from the packaged Botocore data in the pinned Boto3/Botocore wheel. The generator writes two files together:

- `src/aws_safe_agent_cli/aws_botocore_inventory.json`
- `docs/api_coverage.md`

If the pinned SDK version changes, regenerate both files and rerun the full AWS test suite.

The runtime does not load service models from `~/.aws/models` or `AWS_DATA_PATH`. That keeps the coverage claim tied to the package that was tested and mirrored.

## Runtime flow

1. Load `.env` and project settings.
2. Load the generated registry and the Botocore operation model.
3. Validate the input and check the operation’s approval requirements.
4. For a read, check the account and region before calling the AWS operation.
5. For a write, preview offline or use `--bind-aws` to save a plan tied to the AWS connection.
6. Apply only after the current account, role, region, endpoint and request match the reviewed plan. Use one AWS SDK session for the identity check and service request.
7. Record AWS’s response or the reason the result is still unclear.
8. Save redacted run proof under `.state/runs/` unless the caller disables artifacts.

## Verification boundary

Generic generated AWS writes cannot always infer the correct safe read-back operation. When no operation-specific read-back exists, the receipt says verification is `limited` and records the SDK response and plan checks instead of claiming full resource verification.
