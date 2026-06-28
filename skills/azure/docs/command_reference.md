# Command reference

Use these commands when you already know the Azure subscription, resource group, service, and operation you want the agent to inspect or plan. For the guided path, start with [What this skill can help you do](use_cases.md) or [Onboarding](onboarding.md) first, then come back here for exact command shapes.

## Command shape

Global command form:

```bash
qwayk-azure-safe-agent-cli [global flags] <command>
```

Global flags used for safety:

- `--output json|text`
- `--apply`
- `--yes`
- `--plan-out <path>`
- `--plan-in <path>`
- `--receipt-out <path>`
- `--ack-no-snapshot`
- `--ack-irreversible`
- `--env-file <path>`
- `--no-artifacts`

## Discovery

- `qwayk-azure-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-azure-safe-agent-cli inventory summary`

## Auth and tokens

- `qwayk-azure-safe-agent-cli auth check`
- `qwayk-azure-safe-agent-cli auth token set --file token.json`
- `qwayk-azure-safe-agent-cli auth token status`

## Generated Azure operation commands

For each service command, run:

```bash
qwayk-azure-safe-agent-cli <service-command> <operation-name> --input-json <input.json>
```

The command catalog is built from the pinned spec snapshot and split into Azure service-command names and operation names.

## Read flow

Read operations run in one step with token and input JSON:

```bash
qwayk-azure-safe-agent-cli <service> <read-op> --input-json read.json
```

If the command is data-plane, set `AZURE_DATA_PLANE_ENDPOINT` first.

Secret/token/key/password/credential-like reads are marked as `sensitive_read` in the inventory. They run as reads, but the response body values are redacted by default so a provider value returned under a generic field such as `value` is not printed.

## Write flow

Write operations are dry-run first:

```bash
qwayk-azure-safe-agent-cli <service> <write-op> --input-json change.json --plan-out plan.json
```

Apply requires review and all confirmation flags:

```bash
qwayk-azure-safe-agent-cli --plan-in plan.json --apply --yes \
  <service> <write-op> --input-json change.json
```

Add extra acknowledgment flags when needed:

- `--ack-no-snapshot`
- `--ack-irreversible`

## Jobs

- `qwayk-azure-safe-agent-cli jobs run --file jobs.csv`
- `qwayk-azure-safe-agent-cli jobs run --file jobs.csv --plan-out plan.json`

Job files are a local read/dry-run helper. Rows that look like writes are refused in apply mode; use generated Azure operation commands for real writes.

## Run artifacts

- `qwayk-azure-safe-agent-cli runs list`
- `qwayk-azure-safe-agent-cli runs show --run-id <run-id>`

Artifacts include plan JSON, receipt JSON, and summary files under `.state/runs` by default.

## Demo

- `qwayk-azure-safe-agent-cli demo read`
- `qwayk-azure-safe-agent-cli demo write`

The demo write command creates a local dry-run plan only. It does not apply a pretend Azure write path.
