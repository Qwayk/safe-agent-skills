# Azure commands

Use [API coverage](api_coverage.md) to find a service and its operation name. For a first read, follow [the quickstart](quickstart.md).

## Setup and inventory

```bash
qwayk-azure-safe-agent-cli onboarding
qwayk-azure-safe-agent-cli --output json auth check
qwayk-azure-safe-agent-cli inventory summary
```

Use `--env-file <path>` before the command to pick the local settings file. Add `--no-write-env` to onboarding to read the setup steps without creating a file. The token helper uses `auth token set --file token.json` and `auth token status`. [Sign-in and token setup](onboarding.md)

## Run a read

Pass the required path, query and body values in a JSON file. The tool supplies the operation’s pinned API version unless the input specifies one.

```bash
qwayk-azure-safe-agent-cli <service> <operation> --input-json read.json
```

For a direct service request, set `AZURE_DATA_PLANE_ENDPOINT` and use a token for that service. Sensitive reads hide the response values, including values that Azure returns under generic keys such as `value`.

## Save and apply a plan

For this example, save a subscription, resource group and location in `change.json`. The command prepares a plan tied to the current Azure sign-in:

```bash
qwayk-azure-safe-agent-cli resources-management resourcegroups_createorupdate_2025-04-01_148562 --input-json change.json --bind-azure --plan-out plan.json
```

After approval, use the same input:

```bash
qwayk-azure-safe-agent-cli --apply --yes --plan-in plan.json --ack-no-snapshot resources-management resourcegroups_createorupdate_2025-04-01_148562 --input-json change.json
```

Add `--ack-irreversible` or `--ack-spend-money` when the tool requires it and the user approved the risk. Use `--receipt-out <path>` to pick where the receipt is saved. [Approval and receipt steps](safety_model.md)

## Run history

```bash
qwayk-azure-safe-agent-cli runs list
qwayk-azure-safe-agent-cli runs show --run-id RUN_ID
```

Run records usually go under `.state/runs/`. Use `--artifacts-dir` to select a folder, `--output-file` to save the result, or `--no-artifacts` to skip automatic run records. Use `--timeout-s` to set a timeout for this command.
