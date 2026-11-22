# Salesforce commands

Start with [connection setup](onboarding.md) and [a first read](quickstart.md). Use `qwayk-salesforce-platform-safe-agent-cli <family> <action> --help` for the available command flags.

## Common options

- Use `--env-file <path>` and `--output json` before the command to choose the settings file and JSON output.
- Use `--query-param key=value` for more Salesforce query options and `--header key=value` for headers such as `Accept-Language`. The tool sets authorization and content headers.
- Use `--body-file <path>` for JSON, `--data-file <path>` for raw uploads, and `--multipart-file <path>` for a blob-upload manifest.
- Use `--download-to <path>` for supported CSV and binary responses.
- Use `--plan-out` before a write command to save a preview. For an approved apply, use `--apply --ack-no-snapshot`, plus any required `--yes`, `--ack-irreversible`, and `--plan-in` flags. `--receipt-out` sets the receipt path. [Approval rules](safety_model.md)

## Read records and settings

```bash
qwayk-salesforce-platform-safe-agent-cli --output json resources list
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
qwayk-salesforce-platform-safe-agent-cli --output json sobjects-describe get --sobject Account
qwayk-salesforce-platform-safe-agent-cli --output json support knowledge-articles --header Accept-Language=en-US --query-param channel=Pkb
```

## Preview a change

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --plan-out plan.json composite execute --body-file composite.json
qwayk-salesforce-platform-safe-agent-cli --output json sobjects-object create --sobject Document --multipart-file multipart.json
```

After the user approves the first plan and confirms the recovery limit, the matching command is:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json --apply --yes --ack-no-snapshot --plan-in plan.json composite execute --body-file composite.json
```

For import and export commands, see the [bulk jobs guide](jobs_and_batches.md).

## Check previous runs

```bash
qwayk-salesforce-platform-safe-agent-cli runs list --limit 20
qwayk-salesforce-platform-safe-agent-cli runs show --run-id 2026-01-19T104512Z_a3f91c
```

## Where the code lives

The Python package is in `src/salesforce_platform_safe_agent_cli/`. `commands/salesforce.py` owns the named commands, plan checks, and receipts. `cli.py` defines the flags, `config.py` loads settings, `http.py` sends requests, and `runs.py` keeps the local history. See [API coverage](api_coverage.md) for the full command list.
