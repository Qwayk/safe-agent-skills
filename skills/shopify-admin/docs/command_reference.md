# Command reference

Use this page when you need the exact Shopify Admin command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `shopify-admin-api-tool onboarding [--no-write-env]`

## Auth

- `shopify-admin-api-tool --output json --version`
- `shopify-admin-api-tool auth check`

## Operations (pinned inventory)

- `shopify-admin-api-tool operations list`
- `shopify-admin-api-tool operations validate`

## GraphQL queries (explicit)

- `shopify-admin-api-tool query <operation-kebab> [--vars vars.json] [--return-shape-file shape.graphql --ack-unsafe-return-shape]`

## GraphQL mutations (plan-first; explicit)

- Dry-run (plan): `shopify-admin-api-tool mutation <operation-kebab> --vars vars.json [--plan-out plan.json]`
- Apply: currently requires explicit no-snapshot approval before Shopify HTTP when operation-specific saved snapshot support is not available.
- Attempted apply: `shopify-admin-api-tool --apply --yes --plan-in plan.json mutation <operation-kebab> --vars vars.json`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `shopify-admin-api-tool runs list [--limit 20]`
- `shopify-admin-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`
