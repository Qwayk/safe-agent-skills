# Plan review prompt

Use this prompt style when reviewing a `domains add` plan before applying.

## Reviewer prompt

You are checking a GiantPanda plan for a write action.

Inputs:

- User goal
- Plan JSON

Check:

- Is this exactly a GiantPanda domain add for the user-mentioned domains?
- Is the operation `domains add`?
- Is `max_domains <= 100` reflected and all domains properly normalized?
- Are duplicates removed before writing?
- Is plan binding strict (`plan_id`, `safety`, `apply_requirements`, `snapshot_available`, `rollback_supported`)?
- Is `--ack-no-snapshot` required text and warning clear?
- Is the plan file mode `0600` confirmed by checking the saved file metadata? (mode is not inside JSON.)
- Is there one reviewed, unambiguous apply command for this plan?

Return:

- `approve` with the exact required apply command, or
- `reject` with one missing item to fix before apply.
