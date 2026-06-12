# Command reference

This is the full command list for people who want exact syntax.

If you want help deciding what to ask first, start with [What this skill can help you do](use_cases.md), [Set up your account step by step](onboarding.md), and [See how this skill keeps changes safe](safety_model.md).

## Get connected

```bash
qwayk-jobber-safe-agent-cli --output json onboarding [--no-write-env]
qwayk-jobber-safe-agent-cli --output json --version
```

## Check access and auth

```bash
qwayk-jobber-safe-agent-cli --output json auth check
qwayk-jobber-safe-agent-cli --output json auth authorize-url
qwayk-jobber-safe-agent-cli --output json auth token set --file token.json
qwayk-jobber-safe-agent-cli --output json auth token status
qwayk-jobber-safe-agent-cli --output json --apply --yes auth token refresh --refresh-token <refresh_token>
```

## Schema helpers

```bash
qwayk-jobber-safe-agent-cli --output json schema summary
qwayk-jobber-safe-agent-cli --output json schema queries
qwayk-jobber-safe-agent-cli --output json schema mutations
qwayk-jobber-safe-agent-cli --output json schema webhook-topics
```

## Read commands

Read commands are generated from the Jobber Query registry in `docs/api_coverage.md`.

Use one named subcommand at a time:

```bash
qwayk-jobber-safe-agent-cli --output json read clients --selection "nodes { id name } totalCount" --limit 10
```

Optional shared read inputs:
- `--args-json` to pass JSON arguments
- `--args-file` to load JSON args from file
- `--selection` to define GraphQL selection fields
- `--selection-file` for larger selections
- `--limit` for limit/first style paging

## Write commands

Write commands are generated from the Jobber Mutation registry.
Writes are dry-run by default. Live apply requires a saved plan from `--plan-out`, then `--apply --yes --plan-in <plan.json>`.
Some mutations are marked high-risk because no useful before-state is captured. For those, include `--ack-no-snapshot` before live apply. If the mutation is clearly irreversible, also include `--ack-irreversible`.

```bash
qwayk-jobber-safe-agent-cli --output json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json write clientCreate --args-json '{"input": {"firstName":"Acme","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'
```

Shared write inputs:
- `--args-json`, `--args-file`, `--selection`, `--selection-file`
- `--plan-out` to save a plan
- `--plan-in` to apply from a plan
- `--receipt-out` to save an apply receipt
- `--apply --yes --plan-in <plan.json>` required for live apply
- `--ack-no-snapshot` for high-risk mutations that run without a before-state snapshot
- `--ack-irreversible` for irreversible mutations when apply is requested

## Webhook helpers

```bash
qwayk-jobber-safe-agent-cli --output json webhooks topics
qwayk-jobber-safe-agent-cli --output json webhooks verify-signature --body-file payload.json --header X-Jobber-Hmac-SHA256=<header>
qwayk-jobber-safe-agent-cli --output json webhooks verify-signature --body '{"id":"..." , "event":"CLIENT_CREATE"}' --header X-Jobber-Hmac-SHA256=<header>
```

## Job files and runs

```bash
qwayk-jobber-safe-agent-cli --output json jobs run --file jobs.csv
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json jobs run --file jobs.csv
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json jobs run --file jobs.csv
```

```bash
qwayk-jobber-safe-agent-cli --output json runs list --limit 20
qwayk-jobber-safe-agent-cli --output json runs show --run-id <run-id>
```

## Why so much automation in read/write names

The `read` and `write` families are generated from the schema inventory, so command names are official operation names like `read clients` and `write clientCreate`.

Use `docs/api_coverage.md` to confirm full coverage before you ask for a command.
