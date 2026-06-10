# Safety model

This tool separates two checks:

- risk level for the API method
- recovery end state for that write

## Rules

- Dry-run by default; no writes unless `--apply`.
- Refuse when the request is high-risk or irreversible and required confirmations are missing.
- Use output review for every write plan before apply.
- Never log secrets.
- If drift is detected against `--plan-in`, the apply is refused.

- `low`: read-only only.
- `medium`: normal single-resource writes.
- `high`: batch/conflict/linking/move operations.
- `irreversible`: `DELETE` and publish-like operations.

Risk flags and required gates stay as in the code:

- `low`: allowed without `--apply`.
- `medium`: write only needs `--apply`.
- `high`: requires `--apply --yes --plan-in`.
- `irreversible`: requires `--apply --yes --ack-irreversible --plan-in`.

## Verification

The tool keeps verification simple:

- After write, if the response has a `path`, it tries one `GET` verification.
- If verification is not possible, it marks `verification.attempted = false` and keeps the result clear.

Some supported writes also include `before_state` in both the dry-run plan and the apply receipt:

- `update`, `delete`, and publish-like families (`publish`, `set_latest`) are pre-read when possible.
- The tool checks the matching `GET` endpoint before dry-run and before apply when available in discovery.
- It saves a snapshot in the run artifacts directory as `before_state.json`.
- If a read fails, the plan or receipt still keeps `before_state.attempted` true with error details.
- If a mutating family has no matching `GET` endpoint in discovery, live apply is refused for that family.
- Dry-run is still allowed so you can review risk and recovery before a blocked operation.

The tool does not invent extra verification or rollback logic.

## Recovery in plan and receipt

Plans and receipts include a `recovery` object with exactly these top-level end states:

- `rollback_by_inverse_action`
- `irreversible_and_clearly_labeled`

`rollback_by_inverse_action` is only shown when the GTM discovery methods show a direct inverse:

- `family.revert` for create/update/delete
- `family.undelete` for delete
- `family.delete` for create (the `path` is only concrete after apply if returned by the API)

Plans can show a non-ready create rollback plan.
Receipts can show a concrete create rollback plan when the API response includes the created resource path.

The tool does not claim snapshot rollback, generic undo, or broad recovery.
