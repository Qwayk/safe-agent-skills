# Engineering notes

## Regeneration

```bash
.venv/bin/python generate_inventory.py
git diff --exit-code -- specs/manifest.json src/jira_safe_agent_cli/operations.json docs/api_coverage.md
```

Generation stops on a hash change, a count change from 616 Platform or 105 Software operations, an overlapping method-and-path row, or a generated command collision. Review an official spec update before changing the pinned hash or expected count.

## Classification

The generator classifies method-and-path rows, not broad endpoint families. Stable callable rows are implemented and marked live-unverified. Deprecated callable rows remain implemented. OAuth-only rows require bearer auth. Forge-only, Connect-only, experimental, Jira Service Management service-registry, and Jira Operations rows fail closed with their exact status.

POST is a write unless the operation ID or summary is an explicitly recognized read-like Jira operation such as search, count, parse, validate, workflow preview, or bulk fetch. This conservative rule prevents a provider mutation from bypassing the plan gate.

Every write is also checked by the deterministic `HIGH_RISK_PATTERNS` category map. It covers destructive, bulk, permission, membership, workflow, scheme, project-administration, webhook, attachment, notification, sprint-move, and ranking operations, including plural and compound command names. Every DELETE is destructive. `HIGH_RISK_OPERATION_OVERRIDES` keeps governor-proved edge cases explicit and reviewable. `PROJECT_ADMINISTRATION_COMMANDS` explicitly covers project field-context assignment, component, version, and related-work administration without widening ordinary issue, comment, worklog, dashboard, or filter writes. The generated row records its exact reasons, and the inventory invariant test recomputes them for all 360 writes. The current result is 277 stronger-approval writes.

Production targets are fixed before HTTP: Basic auth uses only a root Jira Cloud `*.atlassian.net` site and OAuth uses only `https://api.atlassian.com/ex/jira/<cloudId>`. Saved write plans use schema 2 and a private local HMAC key. Apply checks that signature and independently reconstructs request fields from the selected operation and recorded inputs.

## Package data

`operations.json` is declared as `jira_safe_agent_cli` package data. Installed-wheel tests must prove the inventory contains 721 rows and that representative Platform, Software, gated, read, and write commands still parse outside the source checkout.
