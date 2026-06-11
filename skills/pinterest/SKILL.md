---
name: pinterest-api-safe-cli
description: Run pinterest-api-tool with dry-run by default and no-snapshot approval for writes without saved before-state.
---

This page is the agent-facing rule sheet for the public Pinterest skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Pinterest Qwayk CLI (`pinterest-api-tool`).

Core rules (do not break):
- Default to dry-run plans or read-only previews.
- Live Pinterest writes need a reviewed plan, required risk flags, and `--ack-no-snapshot` when no before-state can be saved.
- Require `--yes` for risky/batch write attempts (this tool requires `--yes` for any remote write attempt).
- Refuse if the target is ambiguous or required config is missing.
- Never print secrets or ask users to paste secrets into chat.
- Plans must show `before_state.status="no_snapshot_available"` when no snapshot can be saved.
- This wrapper has no rollback, restore, or provider backup action for remote writes.
- If a plan or command requires acknowledgement flags (for example `--ack-irreversible`, `--ack-spend`, `--ack-volume`), include them on apply attempts.
- `auth login`, `auth code exchange`, and `auth token set` currently need required approval before token exchange, `.state/token.json` writes, or `.env` updates.

Workflow:
1) Discover (read-only) to identify targets.
2) Dry-run plan (default behavior for writes in this tool).
3) Review the plan (human or Codex).
4) If the user approves apply, pass the explicit flags and collect the receipt or exact tool limitation.
5) Confirm the receipt, verification result, or exact refusal reason after the approved attempt.

References:
- Docs: `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`
- Prefer machine-readable output with `--output json`.

Notes:
- Global flags like `--apply`, `--yes`, and `--output` must come before the subcommand.
- Use command-specific output flags when available (examples: `pins links plan --out <PLAN_PATH>`, `audit snapshot --out-dir <DIR>`).
- For other write plans, capture `--output json` to a file if you need to persist a plan.
- When using auth setup helpers, explain clearly that local token writes need reviewed approval and `--ack-no-snapshot`.
