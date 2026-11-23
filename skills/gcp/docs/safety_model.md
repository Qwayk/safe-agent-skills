# Review and approve Google Cloud changes

Start with a read so you can see what’s there. Before changing anything, show the user the exact resource, what will change, and how you’ll check the result. Changes to access, networking, billing and running services can affect people who use the project.

## Make a plan the user can approve

A write command previews the request by default. For a preview without connecting to Google, leave out `--bind-adc`. That preview says `approval_ready: false`. To save a plan you can apply later, run the same command with `--bind-adc --plan-out plan.json`. That checks Google credentials and the API endpoint without sending the change. If you have an older plan, generate a new one with those flags.

Review the original input alongside the saved plan because the plan hides private values. Confirm the project and resource, Google identity, quota project, operation, exact changes and risk. Include the rollback or restore option if Google supports one for this change. If recovery would be manual or unavailable, say so before asking for approval. Show the exact apply command and wait for the user’s approval.

## Apply the approved request

Use `--input-json` with the same input and pass `--plan-in plan.json --apply --yes`. The tool checks the current operation and safety requirements against the saved plan. It stops if the target, input, identity, quota project or endpoint changed. If anything changed, prepare a new plan for review. Any project, folder, organization, billing account or region limits configured on the machine still apply.

- `--ack-no-snapshot` is required for higher-risk changes that may have no snapshot.
- `--ack-irreversible` is required for changes the tool classifies as irreversible.
- `--ack-spend-money` is required for covered actions that can add charges, such as starting a Compute Engine VM, creating a disk or linking a billing account. Review the expected cost of any proposed change, including ones that carry no spending flag.

## Check what happened

The receipt records the operation, whether it matched the reviewed plan, and what Google reported. Run records normally live under `.state/runs/`. Use `--receipt-out receipt.json` for a specific file. Keep those files private.

| Receipt status | What to do |
|---|---|
| `limited_verification` | Google returned a successful reply. Read the affected resource to confirm the exact change. |
| `pending` | Google accepted the request. Check the operation or resource until you know what finished. |
| `outcome_unknown` | The reply was lost or Google returned a server error. Check the operation history or resource before sending the request again. |
| `operation_failed` or `rejected` | Google reported an error. Read it and check the resource before deciding what to do next. |

Compare what you find with the approved request, including any fields that changed unexpectedly and any before-state or snapshot you saved. The receipt shows `read_back_verified: false` until there is a real read-back check. If you need to repair or reverse a change, make a new plan and ask for approval. [Test results and live checks still needed](proof.md)
