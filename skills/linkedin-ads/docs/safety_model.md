# Safety model

LinkedIn Ads can touch ad accounts, campaigns, creatives, audiences, lead forms, and reports, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the account and campaign first, then review the plan before creative, audience, budget, or campaign changes."

## Core safety rules

This tool runs by reading `spec.safety` from `operation_catalog.py`.

The three safety levels are:

- `read`: live by default.
  - No `--apply` needed.
  - POST can still be here if the endpoint is read-like.
- `write-apply`: plan first, refusal on apply while before-state support is missing.
  - `--plan-out` is needed to review the plan.
  - `--apply --ack-irreversible` reaches the explicit no-snapshot approval.
- `write-apply-yes`: write with extra risk checks.
  - `--apply` and `--plan-out` are needed to make a plan.
  - `--yes` and `--ack-irreversible` are needed on apply.
  - `--plan-in` is needed before the explicit no-snapshot approval.

If required flags are missing, apply stops with `SafetyError`.

All write-capable LinkedIn operation plans now include `before_state.required: true` and `before_state.supported: false`.
This runtime does not capture before-state snapshots or provider backups, so Write applies require explicit no-snapshot approval when no saved snapshot or provider backup is available; missing approval refuses before LinkedIn HTTP.

For all levels, token, token scope, and account permissions still matter at runtime:
- token must exist and be valid,
- product access must match the command,
- LinkedIn may still deny private or tier-gated calls.
