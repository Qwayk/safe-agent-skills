---
name: mercury-api-safe-cli
description: Run mercury-api-tool with dry-run by default and explicit apply/verify gates for local exports/downloads.
---

This page is the agent-facing rule sheet for the public Mercury skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Mercury Qwayk CLI (`mercury-api-tool`).

Core rules (do not break):
- Mercury API calls are GET-only; do not attempt non-GET.
- Default to dry-run; no local file writes without `--apply`.
- Require `--yes` for overwrites and risky/batch local writes.
- Refuse if the target is ambiguous or required config is missing.
- Never print secrets or ask users to paste secrets into chat.
- After apply, verify and return a receipt.

Workflow:
1) Discover (read-only) to identify targets.
2) Dry-run with `--plan-out PATH` (or dry-run by default).
3) Review the plan (human or Codex).
4) Apply with explicit flags.
5) Verify (read-back or idempotence) and save a receipt.

References:
- Onboarding: `docs/onboarding.md`
- Safety model: `docs/safety_model.md`
- Quickstart: `docs/quickstart.md`
- Full CLI reference: `docs/command_reference.md`

Notes:
- Global flags like `--apply` and `--output` must come before the subcommand.
- Store plans and receipts under `.state/runs/` or a user-specified output path.
