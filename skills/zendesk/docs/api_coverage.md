# API coverage (endpoints → CLI)

Purpose:
- Make “all capabilities” measurable (no guessing about what’s implemented).
- Give the Manager a single main reference for review/approval.
- Help customers quickly see what the tool can and cannot do.

Rules:
- Keep this table honest. If something is missing, list it as missing.
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
| Ticketing API (all operations) | One explicit command per OpenAPI operation | `zendesk-api-tool api <operation>` | Plan-only by default. Reads require `--live` to execute. Writes require gates such as `--apply --yes --plan-in`, then require explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available. Deletes also require `--ack-irreversible`. | `tests/test_cli_api_registry.py`, `tests/test_cli_api_safety_gates.py` | No generic/raw request bridge. |

## Known gaps (explicit)

- None currently known for Ticketing OpenAPI coverage. (If Zendesk changes the spec, re-pin a new snapshot and rerun inventory validation.)
