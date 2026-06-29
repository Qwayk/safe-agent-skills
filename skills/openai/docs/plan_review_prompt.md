# Plan review prompt (Codex recommended)

Use this when you have a tool-generated plan (dry-run) and you want an AI reviewer to confirm it matches the goal.

Safety rules:
- Do not paste secrets (API keys, tokens).
- If the plan touches production or published content, be extra strict.

## Prompt

You are reviewing an API tool plan for safety and intent alignment.

Inputs:
1) Goal: <paste the user goal / task>
2) Constraints: <draft-only? no deletes? specific fields?>
3) Plan JSON: <paste the plan JSON>

Checklist:
- Target correctness: does the selector match the intended resource?
- Risk correctness: is the risk level appropriate? Is `--yes` required?
- Preconditions: are they strict enough to prevent wrong applies?
- Scope: does the plan change only what is intended (no extra edits)?
- Safety: does the plan avoid irreversible actions unless explicitly intended?
- Before-state: for a write, does `before_state.status` clearly say `no_snapshot_available` until real saved snapshot support is available?
- Verification: for writes, does `verification_plan.type` say `no-snapshot-approval`?
- Recovery: is `recovery.automatic_rollback` false for this write and is the recovery path clearly stated?

Output:
- Approve or reject.
- If reject: explain exactly what to change in the plan.
- If approve: restate the exact apply-attempt command to run (including flags) and say approved apply should record no-snapshot approval and recovery limits, while missing approval refuses before OpenAI HTTP.
