# Receipt review prompt

Use this after an apply attempt and never paste credentials, tokens, private audio, or private client data.

Inputs:

1. Goal: <paste the goal>
2. Plan JSON: <paste the plan, if available>
3. Receipt JSON: <paste the receipt>

Check that the receipt matches the intended target and request, records the provider result, and includes verification and recovery metadata. If `before_state.status` is `blocked` or `rollback_ready` is false, confirm that the no-snapshot/manual-recovery limit is explicit. A receipt is not a promise that the provider accepted the request or that rollback is available.

Output “accept” or “flag issues” with the next safe action. Do not retry a write automatically.
