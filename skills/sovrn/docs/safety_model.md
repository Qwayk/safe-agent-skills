# How this skill stays safe

This skill is careful in a different way from a write-capable skill.

The main job here is not slowing down before a destructive change. The main job is keeping a read-only Sovrn tool honest about what it can query, which credential type each command needs, and what still is not proved live yet.

## What safety means here

- The shipped command names match real Sovrn Commerce and Advertising endpoints.
- The tool keeps the real auth split visible instead of pretending one key can do every job.
- Secrets stay redacted in output and logs.
- Browser-only JavaScript docs and MCP beta docs are not presented as shipped CLI coverage.
- If local setup is incomplete, the tool should say that clearly instead of guessing.

## Read-only proof loop

For the current read-only surface, the clean proof loop is:

1. Confirm local readiness with `auth check`.
2. Run a real Commerce or Advertising read command.
3. Inspect the returned JSON and the coverage ledger.
4. Save redacted examples in committed docs when the output is stable enough to keep.

## If this tool ever gains writes later

If official write-capable Sovrn endpoints are added later, the tool must return to the normal repo safety pattern:

1. Dry-run by default.
2. Require explicit apply flags.
3. Verify after the change.
4. Save plans and receipts without secrets.

## Local run history

The local run-history helpers stay in place for local audit review and future write-capable additions:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

Read-only commands do not create new run folders today.
