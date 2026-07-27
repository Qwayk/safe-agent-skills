# Jira command guide

## Command shape

Every provider command is fixed by the pinned inventory:

```text
jira-safe [global flags] platform <fixed-command> [documented inputs]
jira-safe [global flags] software <fixed-command> [documented inputs]
```

There are 616 Platform commands and 105 Software commands. Use `jira-safe operations list --limit 721` to list them, `jira-safe operations show --surface platform --command get-issue` to inspect one, or [API coverage](api_coverage.md) for the full ledger.

There is no raw request, URL, method, OpenAPI bridge, SDK pass-through, or arbitrary header command.

## Local and connection commands

```bash
jira-safe onboarding [--auth-mode basic|oauth] [--no-write-env]
jira-safe --env-file .env auth check
jira-safe operations list [--surface platform|software] [--kind read|write] [--status STATUS] [--limit N]
jira-safe operations show --surface SURFACE --command COMMAND
jira-safe --env-file .env runs list [--limit N]
jira-safe --env-file .env runs show --run-id RUN_ID
```

## Read examples

```bash
jira-safe --env-file .env platform get-all-projects
jira-safe --env-file .env platform get-issue --issue-id-or-key PAY-123
jira-safe --env-file .env software get-all-boards --project-key-or-id PAY
jira-safe --env-file .env software get-all-sprints --board-id 42 --state active
```

Each command accepts only parameters documented for its official operation. Run `<command> --help` for its exact flags. Authentication headers are always managed by the configured Basic or bearer credential and are never accepted as command inputs.

## Request bodies and uploads

JSON and JSON Patch operations use a local body file:

```bash
jira-safe --env-file .env --plan-out create-plan.json platform create-issue --body-file examples/create-issue.body.json
```

Text or alternate documented content types use `--content-type`. Multipart operations use repeatable `--file field=path` and `--form name=value` inputs. Jira attachment upload, for example, uses the official multipart command and automatically adds `X-Atlassian-Token: no-check`.

Binary responses are never printed. Use `--response-out FILE`; the JSON result contains the saved path, byte size, and SHA-256 hash.

## Apply a reviewed write

Global safety flags come before `platform` or `software`. Apply accepts the reviewed request only from `--plan-in`, so do not repeat path, query, body, form, or file inputs.

```bash
jira-safe --env-file .env \
  --apply --yes --ack-no-snapshot \
  --plan-in create-plan.json --receipt-out create-receipt.json \
  platform create-issue
```

Add `--ack-high-risk` when the plan says `"high_risk": true`. If a matching before-state GET was planned but fails at apply time, the tool stops; rerun with `--ack-no-snapshot` only after reviewing that new risk.

## Common global flags

- `--env-file FILE`: local Jira configuration.
- `--output json|text`: JSON is the default; JSON mode writes exactly one object to stdout.
- `--timeout-s SECONDS`: request timeout for this run.
- `--verbose`: request method, URL, status, and timing on stderr; never credentials.
- `--plan-out FILE`, `--plan-in FILE`, `--receipt-out FILE`: write review files.
- `--artifacts-dir DIR`, `--run-id ID`: control local write history.
- `--response-out FILE`: save binary response content.
