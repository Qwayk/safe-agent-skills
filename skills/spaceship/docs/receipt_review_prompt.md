# Review a Spaceship receipt

Use the redacted plan and receipt. Do not add credentials or raw private values.

```text
Compare this Spaceship receipt with the approved plan.

User goal:
<goal>

Plan JSON:
<redacted plan>

Receipt JSON:
<redacted receipt>

Check that the operation, selector, plan-integrity digest, request-body digest, HTTP status, async operation ID, and verification result agree with the approved plan. Treat accepted_not_completed as still processing. Treat unverified as unknown final state, not success proof.

Report whether the receipt matches the plan, what Spaceship accepted or completed, what remains unverified, and the safest next read. Do not promise rollback, refund, restore, or undo unless a separate proved provider path exists.
```
