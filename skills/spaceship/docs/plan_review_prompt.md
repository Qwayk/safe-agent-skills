# Review a Spaceship write plan

Do not paste API credentials, transfer authorization codes, raw contact details, checkout links, or private SafePay values into the review.

```text
Review this Spaceship plan before any live change.

User goal:
<goal>

Plan JSON:
<redacted plan>

Check that the operation, domain or other target, request-body digest, critical request fields, risk categories, snapshot or warning, financial recheck status, and required acknowledgements match the goal. Reject the plan if the target is vague, private values are exposed, a price or expiration field changed, the snapshot is stale, or the plan asks for more than the goal.

If the plan is safe, restate the exact apply command with --apply --yes --plan-in and only the acknowledgements listed in required_acknowledgements. Do not claim rollback, refund, restore, or undo unless a separate proved provider path exists.
```
