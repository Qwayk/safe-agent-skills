# cloudflare-api-tool

Customer-ready, safe-by-default CLI for the Cloudflare API.

Current live coverage:
- Named helpers for high-value Cloudflare workflows such as onboarding, auth, accounts, zones, DNS, observability, Browser Run, Workers, Pages, Zero Trust, WAF, storage, and account access.
- Explicit per-operation coverage for the full live official Cloudflare API through `cloudflare-api-tool operations <area> <op_key>`.
- Active allowlist source: `docs/_generated/live_official_api_inventory.json`.
- Active human ledger: `docs/api_coverage_live_official.md`.
- Live official audit on 2026-04-27 UTC found 2,350 official operations, and this CLI now allowlists all 2,350 with explicit commands only.

Safety model:
- No generic raw-call bridge.
- Writes stay dry-run by default and require `--apply`.
- State-changing writes require `--yes`.
- Secret-bearing or destructive operations require `--ack-irreversible`.
- Sensitive reads and sensitive write results are file-only and are never printed to stdout.
- Applied `/accounts*` writes always require `--out`.
- Bulk zone onboarding can use `jobs run`, and `auth zone-create-check` now gives a safe preflight before a real zone-create batch.
- Broad `operations` writes (most of this tool’s generic surface) do not have tool-owned rollback or restore paths today.
- If a command has built-in recovery guidance, it appears as a narrow `rollback_plan` section in that command’s own receipt (currently mainly in some Workers commands).

Start here:
- `docs/onboarding.md`
- `docs/safety_model.md`
- `docs/command_reference.md`
- `docs/api_coverage.md`
- `docs/proof.md`

Live audit artifacts:
- `docs/api_coverage_live_official.md`
