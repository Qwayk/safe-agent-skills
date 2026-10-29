# Agent extension guide

Goal: make it easy (and safe) for an AI coding assistant to extend this tool.

## Repo map

- `src/google_ads_api_tool/cli.py`: CLI wiring
- `src/google_ads_api_tool/commands/`: command handlers
- `src/google_ads_api_tool/config.py`: `.env` parsing and validation
- `src/google_ads_api_tool/google_ads_client.py`: client construction + proto conversion helpers
- `src/google_ads_api_tool/rpc_commands.py`: explicit per-RPC-method command registration + handlers
- `src/google_ads_api_tool/rpc_v25_registry.py`: generated v25 RPC method registry (main reference for CLI surface)
- `src/google_ads_api_tool/protobuf_json.py`: strict JSON→protobuf request parsing
- `src/google_ads_api_tool/output.py`: stdout contract (one JSON object)
- `src/google_ads_api_tool/audit_log.py`: JSONL audit log
- `tests/`: unit tests (prefer mocks, no real network)

## Add a read command

1) Create `src/google_ads_api_tool/commands/<name>.py`.
2) Implement `cmd_<name>(args, ctx) -> int`.
3) Register in `cli.py`.
4) Emit exactly one JSON object in JSON mode.
5) Add a unit test for output shape and edge cases (mock-only).

## Add or modify a write command (safety contract)

This tool supports external writes, but every write must remain safe-by-default:
- Plan-first (no `--apply` → deterministic plan object)
- Apply requires explicit approvals (`--apply` + additional gates per risk class)
- Customer-id allowlist default-deny + global kill switch
- Supported live writes must save before-state before mutation.
- Readable `CampaignCriterion` ad-schedule removes are supported when before-state is saved first.
- Create/upload, unreadable removes, and other unsupported write shapes need explicit no-snapshot approval support or a true blocker reason before live apply.
- Deterministic plan fingerprint + drift check when applying from `--plan-in`
- Best-effort read-back verification after apply (when possible)

If you change the write workflow, update in the same change set:
- `docs/safety_model.md`
- `docs/api_coverage.md`
- `docs/proof.md`
- `docs/examples/outputs/` (synthetic plan/receipt/refusal examples)
- `tests/test_rpc_surface_coverage.py` (surface enforcement)
