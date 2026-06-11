# API coverage

Purpose:
- Make the Cloudflare API coverage claim exact and auditable.
- Keep one active runtime allowlist reference.
- Separate live coverage from historical phase ledgers.

## Current truth

- Provider: Cloudflare
- API base URL: `https://api.cloudflare.com/client/v4/`
- Live audit date (UTC): `2026-04-27`
- Official live source: Cloudflare API sitemap plus official method pages only
- Official effective operations found: `2350`
- Active CLI allowlisted operations: `2350`
- Coverage claim status: true for the live official API as of `2026-04-27`

## Active coverage sources

- Runtime allowlist JSON: `docs/_generated/live_official_api_inventory.json`
- Human ledger: `docs/api_coverage_live_official.md`
- Live official coverage ledger: `docs/api_coverage_live_official.md`

## What changed in the live audit

- Deprecated live operations still present in official docs: `5`

The per-operation evidence is summarized in the generated coverage ledgers.

## Safety contract

- Every live operation is exposed through an explicit allowlisted command only: `cloudflare-api-tool operations <area> <op_key>`.
- Named front doors can sit on top of those allowlisted operations for common workflows (for example `browser-run ...` for Browser Rendering quick actions).
- There is no raw request bridge.
- Sensitive reads and sensitive write results stay file-only.
- State-changing writes stay plan-first and require `--apply --yes`.
- Secret-bearing or destructive operations require `--ack-irreversible`.
- Applied `/accounts*` writes require `--out`.

## Historical ledgers

Historical `docs/api_coverage_*.md` ledgers are kept for older proof references.
They are no longer the active runtime allowlist reference.
