# Proof and verification

Use this page when you want the clearest proof story for Qdrant Cloud.

This repo does not rely on live Qdrant Cloud credentials for normal proof. The evidence here comes from the local suite, the committed redacted examples, and the explicit live-gating and write-gating behavior.

## What is already proved

- The command surface is explicit and inventory-backed.
- No real Qdrant Cloud network call happens unless `--live` is present.
- Ordinary writes stay plan-first and require explicit no-snapshot approval when no saved before-state or provider backup exists.
- Provider backup and restore workflows keep a separate recovery contract from ordinary writes.
- The committed examples show version, read, plan, refusal, and provider-backup receipt shapes.

## Last checked

- Local docs and contract alignment rechecked: **2026-06-11 UTC**
- Local suite and example proof baseline: **2026-06-04 UTC**
- Tool version: `0.1.0`
- Inventory version: `v1`

No live Qdrant Cloud credentials are stored here, so this proof pack stays local-first and redacted on purpose.

## Core validation

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
qdrant-cloud-api-tool --output json --version
qdrant-cloud-api-tool --output json auth check
python3 scripts/generate_example_outputs.py
```

## Committed examples

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/read.example.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
- `docs/examples/backup_restore.plan.example.json`
- `docs/examples/backup_restore.receipt.example.json`

The current `receipt.example.json` is still an ordinary-write refusal example, not a claim that every live write path already has recovery support.

## What can still go wrong

- missing `--live` on a real API read
- missing or wrong API key
- wrong account ID, cluster ID, or backup ID
- missing destructive or spend acknowledgements
- ordinary writes that still have no saved before-state or provider backup

## How to verify the risky parts

- If a live read fails, check the key, account scope, and whether `--live` was present.
- If an ordinary write refuses, confirm the refusal happened before Qdrant Cloud HTTP.
- If a plan is being reviewed, check the account, cluster, request payload, and recovery contract.
- If a provider backup or restore workflow is used, check the receipt and the verification fields after apply.

## Intentional limits

Not covered on purpose:

- generic rollback claims for ordinary writes
- hidden live network calls
- fake recovery promises where the product does not expose a real recovery path
