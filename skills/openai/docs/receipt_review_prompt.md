# Receipt review prompt (Codex recommended)

Use this after a live read receipt, or after a future snapshot-backed write receipt, to confirm execution matched the plan and verification passed.

Safety rules:
- Do not paste secrets (API keys, tokens).
- If verification failed, do not rollback automatically; review first.

## Prompt

You are reviewing an API tool receipt.

Inputs:
1) Goal: <paste the user goal / task>
2) Plan JSON (if available): <paste the plan JSON>
3) Receipt JSON: <paste the receipt JSON>

Checklist:
- Did the tool apply the intended changes (matches the plan)?
- Did verification pass? If not, what failed?
- Any unexpected changes or extra fields modified?
- Is recovery explicit in `receipt.recovery`? If `automatic_rollback` is false, confirm the manual recovery plan is clear.
- If the tool produced `recovery.backups` or `recovery.snapshots`, list what to inspect.
- If this was a current write attempt, confirm the receipt records either a saved before-state or explicit no-snapshot approval when no saved snapshot is available.

Output:
- Accept or flag issues.
- If issues: propose next action (re-plan, explicit recovery steps, or manual fix).
