---
name: wordpress-api-safe-cli
description: Run wordpress-api-tool with dry-run by default and explicit apply/verify gates.
---

This page is the agent-facing rule sheet for the public WordPress skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the WordPress Qwayk CLI (`wordpress-api-tool`).

Core rules (do not break):
- Default to dry-run; no writes without `--apply`.
- Require `--yes` for risky/batch writes.
- Refuse if the target is ambiguous or required config is missing.
- Never print secrets or ask users to paste secrets into chat.
- After apply, verify and return a receipt.

Workflow:
1) Discover (read-only) to identify targets.
2) Dry-run with `--plan-out PATH` (or dry-run by default).
3) Review the plan (human or Codex).
4) Apply with explicit flags.
5) Verify (read-back or idempotence) and save a receipt.

6) When present, read the `rollback_plan` field in the receipt for manual inverse steps.

References:
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`
- Global flags like `--apply` and `--output` must come before the subcommand.

Notes:
- Store plans and receipts under `.state/runs/` or a user-specified output path.
