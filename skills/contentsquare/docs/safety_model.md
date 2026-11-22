# Approvals and receipts

Read export jobs and runs, metrics, and Speed Analysis reports without applying a change. Downloads save a local file. Creating a job, sending an enrichment batch, or changing an event needs a saved plan and your approval.

## Before a change

1. Run the intended write command with `--plan-out` and without `--apply`. The CLI saves the plan without contacting Contentsquare.
2. Check the action, project, integration or event when relevant, and the exact request. If you use a project-level credential without a project ID set locally, confirm its assigned project before approving. Check what you can verify afterward and whether the change can be undone.
3. After approval, run the same action with `--plan-in`, `--apply` and `--yes`. If the command, settings, requested changes, or connection changed, make a fresh plan. Plans made before these checks were added also need a fresh preview. Use the same project and other request flags. The CLI can read the body from the saved plan.

| Command | Extra confirmation |
| --- | --- |
| `data-export create-job` | Use the saved plan and standard confirmation. |
| `enrichment send-batch` | Add `--ack-no-snapshot`. |
| `speed-analysis event-create` | Add `--ack-no-snapshot`. |
| `speed-analysis event-delete` | Add `--ack-irreversible`. |

If a command returns `refused: true`, read `reasons`. The CLI stopped before sending the change.

## After a change

Read the receipt beside the plan. Check that the reply matches what you asked for and look for any unexpected result. The CLI sends an approved change once per apply. Here is what the receipt can tell you:

- **`accepted`** means Contentsquare accepted the request. Check the result before treating the work as complete. For an export, follow the command in `follow_up` to list runs for that job.
- **`rejected`** means Contentsquare returned a failure in the reply. Use that reply to see what needs fixing.
- **`uncertain`** means the reply was lost or did not confirm what happened. Check Contentsquare before trying again. For a new export with no returned ID, check the project’s jobs.

Some changes have no documented way to undo them. If a follow-up change is needed, show the proposed fix and get approval first.

Use `--receipt-out` to choose a receipt file. Write-capable commands can also save plans, receipts, summaries and audit logs under the local `.state/runs/` folder. Keep these files private, especially when a request includes behavioral data.
