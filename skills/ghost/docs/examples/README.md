# Examples (redacted)

This folder contains **committed, redacted** example artifacts to support “proof-first” publishing and troubleshooting.

Rules:
- Never include secrets (API keys, tokens, Authorization headers).
- Use `example.com` / `https://example.com` for domains.
- Use fake IDs and slugs.
- These files should be representative of real outputs/plans/receipts, but safe to publish.

Contents:
- `outputs/`: complete stdout JSON objects from real CLI invocations (redacted)
- `plan.example.json`: representative dry-run plan with `snapshot_plus_restore` recovery metadata (redacted)
- `receipt.example.json`: representative apply receipt with snapshot evidence and manual-restore pointers (redacted)
