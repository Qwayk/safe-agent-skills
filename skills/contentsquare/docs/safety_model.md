# Safety model

Contentsquare work can expose sensitive behavior data, create export jobs, send enrichment batches, or change Speed Analysis events. This skill is built around a simple rule: look first, review second, change last.

Safe use should feel calm. The agent checks the account and project, explains what it found, shows a plan before risky work, and leaves a record after live work. Secrets stay local.

A good safety ask is: "Check the Contentsquare project, endpoint, request body, risk, and approval step before any live change, then tell me whether verification will be full read-back or limited provider-response verification."

## Read-only work

Metrics, object lists, export job reads, export run reads, and Speed Analysis report/list operations return data without changing Contentsquare state.

## Plan-first writes

These commands are dry-run by default:

- `data-export create-job`
- `enrichment send-batch`
- `speed-analysis event-create`
- `speed-analysis event-delete`

Dry-run writes save a plan when `--plan-out` is used. Live apply requires `--plan-in --apply --yes`.

## No-snapshot acknowledgements

Enrichment sends and Speed Analysis event writes do not have a universal safe before/after snapshot in the official docs. The CLI requires `--ack-no-snapshot` for those writes. Event deletes also require `--ack-irreversible`.

## Proof files

Write-capable commands can save plans, receipts, audit logs, and summaries under `.state/runs/`. These files are local, gitignored, and should never contain secrets.

## If the target changes after planning

When applying from a saved plan, the tool should refuse if the reviewed target no longer matches. Examples include a different project, integration id, job id, event body, endpoint, or request body.

If the target changed, make a new plan.

## Recovery and follow-up

Do not assume a Contentsquare change can be undone. Some actions can be checked after the provider responds, some actions need manual follow-up in Contentsquare, and some actions do not have a safe universal before/after snapshot in the official docs.

If verification fails and a safe follow-up action exists, create a new plan and require approval. If no safe follow-up exists, the tool should say that plainly before the user approves the risky work.
