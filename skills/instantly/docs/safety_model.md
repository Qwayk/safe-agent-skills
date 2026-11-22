# Approve changes and check results

An agent can read ordinary campaign data directly when it has permission for the job. Ask it to show the workspace, target and proposed change before it runs a write.

## Review the preview

- Run the command without `--apply` to preview a change. Use `--plan-out <file>` when you need a named copy to review.
- Check the campaign, leads, or other target and what will change. For bulk work, check the input file and the number of rows. Check which evidence the CLI can save and what you would need to fix by hand.
- Apply only after the user approves. High-risk or batch changes use `--apply --yes`. Starting or resuming a campaign uses both flags and a matching saved plan supplied by `--plan-in`. Pausing uses the existing `--apply` step after approval.
- Commands such as deletes and sending replies also require a saved plan. Where required, irreversible changes need `--ack-irreversible`. Approve `--ack-no-snapshot` explicitly when the CLI cannot save the old state. For the exact command and flags, see the [command reference](command_reference.md).
- Apply a saved plan using the same API address and key used for the preview. The CLI stores a fingerprint to check the connection without saving the key. If the key changes or a plan predates this check, save a new preview.

## Read the receipt

Check `refused` and `reasons` first. A refused command stopped before the requested change, even if the tool returned exit code 0. After a write, check the receipt against the preview and see what Instantly confirmed.

A campaign status receipt checks the same campaign. It marks activation verified only when Instantly shows it as active, and pausing only when it shows as paused. If the status still differs or the check fails, check Instantly before trying again.

A bulk import receipt shows the counts Instantly reported for each batch. `all_added` tells you whether Instantly reported adding every input row. If a reply goes missing, the receipt keeps counts from earlier batches, shows the batch that needs checking and lists how many were still unsent. Check the outcome before retrying. Use the same saved plan and unchanged input so the CLI sends the same request key for each batch. [Bulk import commands](command_reference.md#add-leads-in-bulk)

The CLI saves the previous result for supported writes in `.state/runs/<run_id>/before/` next to the settings file. Use it to review the change or repair it by hand. The CLI has no automatic undo. Find recent runs with `runs list` and their files with `runs show --run-id <id>`.

## Keep private output local

- Keep API keys, passwords and credentials out of chat, command examples, plans and audit logs.
- Sensitive account reads such as `accounts list`, `accounts get` and `accounts ctd-status` need `--apply --yes` and write their result to a local receipt. Use the path from `receipt_out`.
- `api-keys create` needs `--plan-in` and `--ack-store-secret-locally`. `dfy-email-account-orders list-accounts --with-passwords` also needs `--ack-store-secret-locally`. Returned secrets stay in `.state/sensitive/`. The CLI returns the path, a fingerprint and available non-secret details.
