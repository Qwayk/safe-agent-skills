# Safety model

This tool has two modes:

- Read checks (`auth`, `domains stats`)
- Write plan/apply flow (`domains add`)

## Reads

- `auth check` is local-only and never sends a request.
- `domains stats` is a direct read call against the fixed host with your token.
- Redirect responses are refused rather than followed.

Stats responses can still contain useful business values and are treated as private artifacts for this tool.

## Write flow for domain add

`domains add` is local plan-first by default.

1. A plain call creates a local plan only and writes a private 0600 plan file.
2. Apply can only proceed when all gates are present:
   - `--apply`
   - `--plan-in <plan_path>`
   - `--approve-plan <exact_plan_id>`
   - `--ack-no-snapshot`
3. The tool checks that plan operation, endpoint, host, plan id, safety metadata, and domain list match before sending.

## No snapshot / rollback

There is no documented rollback, restore, or undo flow for `domains add`.
Every apply requires `--ack-no-snapshot`, and the no-snapshot warning is included in plan and receipt metadata.

## Plan and receipt integrity

- Plan and receipt files are private and written with mode `0600`.
- The plan id binds the exact normalized domain list, host, endpoint, operation, 100-domain limit, and reviewed duplicate-removal metadata.
- Apply verifies exact host/operation/id/domain alignment and refuses drift.

## Post-write parse behavior

If provider output on apply is not valid JSON, the tool does not retry automatically.
You should inspect the GiantPanda dashboard or account UI manually because this tool has no dedicated post-write readback endpoint for add verification.
