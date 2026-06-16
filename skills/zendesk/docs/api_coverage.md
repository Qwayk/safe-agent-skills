# API coverage

Zendesk coverage shows exactly what the shipped commands can do with tickets, users, organizations, groups, macros, jobs, and support content. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether the shipped commands can inspect tickets, users, and macros, then show which support changes are covered."

## Coverage notes

- Give the Manager a single main reference for review/approval.
- Help customers quickly see what the tool can and cannot do.
- If behavior differs from the provider docs, note it and link `docs/references.md`.

## Summary

- Provider: Zendesk Support (Ticketing) API
- API base URL: `https://{subdomain}.zendesk.com` (or `ZENDESK_BASE_URL`)
- Auth method: API token (email + token via HTTP Basic auth) or OAuth bearer token
- Pinned OpenAPI snapshot: `docs/official_openapi_ticketing_2026-03-05.yaml`
- Pinned operation inventory: `docs/official_operations_ticketing_2026-03-05.txt`
- Pinned command inventory: `docs/official_commands_ticketing_2026-03-05.txt`
- Total operations in snapshot: 595
- Last audited (UTC): 2026-06-04

## Endpoint coverage

Columns:
- Endpoint
- Capability
- CLI command(s)
- Safety gates (dry-run/apply/yes)
- Tests/examples
- Notes

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| OpenAPI snapshot (pinned) | Canonical operation + command inventory | `zendesk-api-tool inventory ...` | read-only | `tests/test_inventory.py` | Offline; proves 100% coverage is measurable. |
| Ticketing API (all operations) | One explicit command per OpenAPI operation | `zendesk-api-tool api <operation>` | Plan-only by default. Reads require `--live` to execute. Writes require gates such as `--apply --yes --plan-in`, then require explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available. Deletes also require `--ack-irreversible`. | `tests/test_cli_api_registry.py`, `tests/test_cli_api_safety_gates.py` | No generic/unreviewed direct API passthrough. |

## Known gaps (explicit)

- None currently known for Ticketing OpenAPI coverage. (If Zendesk changes the spec, re-pin a new snapshot and rerun inventory validation.)
