# Proof pack (publish-ready evidence)

Purpose:
- Capture minimal, customer-auditable evidence: what ran, what came back, and what safety gates exist.

Rules:
- Never include secrets (API keys/tokens, Authorization headers).
- Keep examples redacted and deterministic.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: Codex + Spark builder review (offline stub)
- Tool version: 0.1.0
- Inventory version: `v1` (from vendored `qdrant-cloud-public-api` protos)
- Environment: offline local stub (no real Qdrant Cloud calls in this repo task)

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `qdrant-cloud-api-tool --output json --version`

3) Auth/config check:
- `qdrant-cloud-api-tool --output json auth check`
- `qdrant-cloud-api-tool --output json --live auth check`

4) Generate offline example outputs (local stub):
- `python3 scripts/generate_example_outputs.py`

5) One provider-backup recovery plan example (no network):
- `qdrant-cloud-api-tool --output json cluster-backup-v1 restore-backup --account-id 00000000-0000-0000-0000-000000000000 --backup-id 11111111-1111-1111-1111-111111111111 --request-json docs/examples/backup_restore.request.example.json --plan-out backup_restore.plan.json`

2026-06-04 Codex validation: focused safety suite 10 tests OK; full suite 20 tests OK; docs formatting 2 tests OK; version smoke passed; example generator passed; committed JSON examples parsed.

## Example outputs (committed, redacted)

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/read.example.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (ordinary write refusal example; old filename kept)
- `docs/examples/backup_restore.plan.example.json`
- `docs/examples/backup_restore.receipt.example.json`

## What can go wrong (and how we verify)

- **Forgot `--live`** → apply refuses as a safe no-op (`refused=true`).
- **Missing high-risk acknowledgements** → DELETE and payment/billing actions refuse unless required flags are present.
- **Plan drift** → `--plan-in` apply refuses if env or request hash differs from the reviewed plan.
- **Ordinary write safety drift** → write apply requires explicit no-snapshot approval before Qdrant Cloud HTTP when no saved snapshot is available until `safety.before_state.supported` is true or provider-backup capture exists for that operation.
- **Recovery contract mismatch** → plan/refusal/provider receipt includes explicit safety fields; ordinary writes are `no-recovery`, backup/restore family is `provider-backup-restore`.
- **Wrong recovery family assumption** → verify backup/restore examples use the provider-backup contract while ordinary create/update examples stay `no-recovery` and require explicit no-snapshot approval before provider HTTP.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
