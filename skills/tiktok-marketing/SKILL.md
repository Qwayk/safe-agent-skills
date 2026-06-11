---
name: tiktok-marketing-safe-cli
description: Run tiktok-marketing-api-tool safely with plan-first workflows, review gates, and explicit auth checks.
---

This page is the agent-facing rule sheet for the public TikTok Marketing skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the TikTok Marketing API CLI: `tiktok-marketing-api-tool`.

Core rules (do not break):
- Always use `--output json`.
- Never print or request secrets.
- Refuse if required config is missing or the target is unclear.
- Treat all API operations as either:
  - plan-only (read) unless `--live` is set, or
  - write requiring `--live --apply --yes --plan-in --ack-irreversible`.
- For write actions, require `--apply --yes --plan-in --ack-irreversible` and a reviewed plan.
- Write apply needs a reviewed plan and `--ack-no-snapshot` when no before-state can be saved. Expect `before_state.status="no_snapshot_available"` before approval and a receipt after supported approved writes.

Workflow:
1) Validate auth and readiness:
   - `tiktok-marketing-api-tool --output json auth check`
2) Discover supported operations and confirm target:
   - `tiktok-marketing-api-tool --output json api ops list`
   - `tiktok-marketing-api-tool --output json api ops show --op <operation_command>`
3) Build a plan first:
   - `tiktok-marketing-api-tool --output json api <operation_command> --query-json ...`
4) Apply only when user has approved and all gates are present:
   - `tiktok-marketing-api-tool --output json --live --apply --yes --plan-in plan.json --ack-irreversible api <operation_command>`
5) Return the refusal output and any saved plan/run paths for audit.

Read-only checks:
- `tiktok-marketing-api-tool --output json api <operation_command> --query-json ...`
- `tiktok-marketing-api-tool --output json runs list --limit 20`
- `tiktok-marketing-api-tool --output json runs show --run-id <RUN_ID>`

Docs and safety notes:
- Authentication notes: `docs/authentication.md`
- Runtime reference: `docs/command_reference.md`
- Coverage and access gates: `docs/api_coverage.md` and `docs/proof.md`
