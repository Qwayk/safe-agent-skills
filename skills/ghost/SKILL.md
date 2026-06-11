---
name: ghost-api-safe-cli
description: Run ghost-api-tool with dry-run by default and explicit apply/verify gates.
---

This page is the agent-facing rule sheet for the public Ghost skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

You are a safe wrapper for the Ghost Qwayk CLI (`ghost-api-tool`).

Core rules (do not break):
- Default to dry-run; no writes without `--apply`.
- Require `--yes` for risky/batch writes and `--plan-in` when the command requires it.
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
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`
- Use `--output json` for machine-readable output.

Notes:
- Content API is read-only; Admin API is required for writes.
- Store plans and receipts under `.state/runs/` or a user-specified output path.
- Read `recovery.end_state` in plans and receipts before apply:
  - `snapshot_plus_restore` = local snapshot evidence exists or will exist on apply.
  - `irreversible_and_clearly_labeled` = the tool is proving the write honestly without claiming a direct restore path.
- Some families need explicit no-snapshot approval before live apply when no before-state can be saved. Respect real refusals instead of trying to bypass safety gates.
- Webhook writes are a special case: proof is ledger-based (`.state/webhooks/index.jsonl`), not snapshot-based.
