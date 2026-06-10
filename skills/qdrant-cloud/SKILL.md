# Skill: Qdrant Cloud API (safe CLI)

This page is the agent-facing rule sheet for the public Qdrant Cloud skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill uses `qdrant-cloud-api-tool`, a safety-first CLI for the Qdrant Cloud control-plane API.

## Safety rules (must follow)

- Never make network requests unless the user explicitly requested live API access and you included `--live`.
- For any non-GET operation, default to plan-only (no `--apply`) and ask for a review of the plan output before applying.
- For apply:
  - Ordinary writes currently need required approval before Qdrant Cloud HTTP after `--live --apply`.
  - High-risk writes require `--live --apply --yes` and the required acknowledgement flags.
  - DELETE-like operations require `--ack-irreversible --plan-in`.
  - Payment/billing operations require `--ack-spend-money --plan-in`.
  - Provider backup/restore workflows can apply live only for `create-backup`, `restore-backup`, and `create-cluster-from-backup`.
- Never print or store API keys. Do not paste `.env` contents into chat.
- All write plans show `safety.before_state` and a recovery contract:
  - Ordinary writes are marked `no-recovery` and `before_state.supported: false`.
  - Backup/restore-family commands are marked `provider-backup-restore` and must be run as explicit provider workflows.
- Do not infer automatic rollback. If recovery is needed, use the explicit contract in the plan, refusal, or provider receipt.

## Where to find the official command list

- Canonical inventory: `docs/official_commands_v1.txt`
- Coverage mapping: `docs/api_coverage.md`

## Typical workflows

1) Onboarding:
- `qdrant-cloud-api-tool onboarding`
- `qdrant-cloud-api-tool --output json auth check`

2) Read:
- `qdrant-cloud-api-tool --output json --live <domain> <command> ...`

3) Ordinary write (plan -> no-snapshot approval/result):
- Plan: `qdrant-cloud-api-tool --output json <domain> <command> ... --request-json request.json --plan-out plan.json`
- Apply request: `qdrant-cloud-api-tool --output json --live --apply --plan-in plan.json <domain> <command> ... --request-json request.json --receipt-out receipt.json`

4) Provider backup/restore:
- Plan first, then apply only the explicit backup/restore command after review.
