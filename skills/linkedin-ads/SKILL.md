---
name: linkedin-ads-safe-cli
description: Run linkedin-ads-api-tool with required safety gates, family/operation commands, and review flows.
---

This page is the agent-facing rule sheet for the public LinkedIn Ads skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for `linkedin-ads-api-tool`.

Core rules:
- Always run commands with `--output json`.
- Do not ask for token values in prompts.
- If setup looks missing, start with:
  - `linkedin-ads-api-tool onboarding`
  - `linkedin-ads-api-tool --output json auth check`
- Read commands run live.
- `write-apply` commands are planned first (use `--plan-out`) and currently need required approval before LinkedIn HTTP after `--apply --ack-irreversible`.
- High-risk write commands are `write-apply-yes` and require `--apply`, `--yes`, `--plan-in`, `--ack-irreversible`, and no-snapshot approval when no before-state can be saved.
- Keep approvals visible: `access-gated`, `private-api-gated`, `tier-gated`, `live-unverified`.
- Use `docs/api_coverage.md` for supported families and operations.

Workflow:
1) Confirm auth setup.
2) Check allowed operation in `docs/api_coverage.md`.
3) Run plan for write commands:
   - `linkedin-ads-api-tool --output json --plan-out plan.json <family> <operation> ...`
4) Confirm the receipt or exact refusal reason with matching gate flags after review.
   - Standard write: `linkedin-ads-api-tool --output json --apply --ack-irreversible <family> <operation> ...`
   - High-risk: `linkedin-ads-api-tool --output json --apply --yes --plan-in plan.json --ack-irreversible <family> <operation> ...`

Allowed output checks:
- `linkedin-ads-api-tool runs list`
- `linkedin-ads-api-tool runs show --run-id <id>`
