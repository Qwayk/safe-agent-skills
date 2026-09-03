# Plan review prompt

Review the plan below without using or requesting credentials.

Inputs:

1. Goal: <paste the goal>
2. Constraints: <paste constraints>
3. Plan JSON: <paste the plan>

Check:

- Is the selector and endpoint correct?
- Are risk and required approvals accurate?
- Does the plan show `before_state.status` as a real saved state or `blocked` with a clear reason?
- Does verification describe a concrete read-back or output check?
- Does recovery state whether rollback exists? If `rollback_ready` is false, is the manual cleanup limit explicit?
- Is the command limited to the intended ElevenLabs operation?

Output “approve” or “reject” with the exact change needed. If approved, restate the exact apply command, including `--live --apply` and any required spend, irreversible, yes, and no-snapshot approvals. Approval is review evidence, not proof of live provider success.
