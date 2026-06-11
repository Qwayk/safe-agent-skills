# How this skill stays safe

Freepik licensed downloads are treated as state-changing work because they can:

- create a provider download record
- attach a license record to your account
- write a local file
- append a row to the inventory CSV

## Default behavior

- `download` is dry-run by default.
- `jobs run` does not start unless you pass both `--apply` and `--yes`.
- Licensed live download also needs `--ack-no-snapshot` because this tool does not save a reliable before-state snapshot for that write family.

## Before-state truth

The real before-state contract today is:

- `before_state.required=true`
- `before_state.supported=false`
- `before_state.status=no_snapshot_available`
- `before_state.approval_required=--ack-no-snapshot`

That means live download is allowed only after an explicit no-snapshot approval. It does not mean the tool has a saved restore point.

## What dry-run gives you

Dry-run download returns:

- the planned resource ID and format
- preview and resource URLs
- the no-snapshot before-state contract
- the after-apply verification plan
- the irreversible recovery contract

Dry-run does not call the licensed download endpoint or write files.

## What approved apply gives you

Approved apply returns:

- the downloaded row or rows
- the same no-snapshot before-state contract
- a `no_snapshot_approval` record
- verification details
- the irreversible recovery contract

Approved apply writes the local file and the inventory CSV row.

## Recovery wording

Licensed downloads are irreversible in this CLI:

- `end_state=irreversible_and_clearly_labeled`
- `strategy=no_inverse`
- `rollback_ready=false`
- `automatic_rollback=false`
- `rollback_plan=null`

That is why the tool slows down before live download instead of promising undo that it does not have.

## Additional guardrails

- `download` refuses unless the resource detail clearly shows `is_ai_generated=false` and `has_prompt=false`.
- If `(resource_id, format)` already exists in the inventory CSV, the tool refuses unless you pass `--force`.
- If the destination file already exists, the tool refuses unless you pass `--force`.
- Approved apply records the local file hash in the inventory row.

## Local helper writes

These are separate from licensed downloads:

- `--write-jobs` writes a local jobs CSV only
- `preview --save-preview` writes local preview files only

Delete those local helper files manually when you no longer need them.
