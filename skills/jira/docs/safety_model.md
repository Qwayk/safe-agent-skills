# How Jira changes stay under your control

## Reads run after validation

An operation classified as a read can call Jira after the tool validates the site URL, credential, fixed command, required path inputs, and documented query inputs. The tool does not accept an arbitrary URL or method.

## Writes stop at a saved plan

Without `--apply`, every write creates a mode-`0600` JSON plan and sends no Jira request. The plan fixes the site, named command, HTTP method, resolved path, query, documented headers, body-file hash, upload-file hashes, risk level, and snapshot availability. A private mode-`0600` key beside the selected `.env` file signs the complete plan.

Apply reads the request only from that saved plan. It checks the local signature, reconstructs the path, query, headers, and snapshot query from the recorded fixed-command inputs, and checks the body descriptor against the operation's official content types. Editing and rehashing a plan cannot change request or safety fields. Operation input flags are refused during apply so they cannot quietly replace reviewed values. If a referenced body or upload file changes after planning, apply stops.

## Before-state and no-snapshot approval

For PUT, PATCH, and DELETE operations with a callable GET on the same official path, apply tries that GET first and saves `before.json`. If the read fails, the write stops unless you explicitly accept the missing snapshot with `--ack-no-snapshot`.

Creates, actions, bulk submissions, and other operations without a reliable generic read show a no-snapshot warning in the plan. Apply requires `--ack-no-snapshot` for those operations.

## Stronger approval

All writes need `--apply`, `--plan-in`, and `--yes`. The generated inventory requires `--ack-high-risk` for 277 of 360 writes covering destructive, bulk, permission, membership, workflow, scheme, project-administration, webhook, attachment, notification, sprint-move, and ranking categories. The coverage ledger records the reason on every marked operation.

These flags must appear before the Platform or Software command because they apply to the whole reviewed run.

## Verification and receipts

When a write has the matching GET path, apply reads the target again. For deletes, HTTP 404 is the expected verification. Other matching-path writes are verified when the GET succeeds.

Every provider apply attempt writes a private redacted receipt. The receipt records the command, plan signature, target path, provider status, snapshot result, approvals, and verification result. It does not record credentials, authorization headers, or the signing key.

The tool does not promise rollback or undo. Before-state and receipts help review what happened, but many Jira changes require a separate approved Jira operation to reverse.
