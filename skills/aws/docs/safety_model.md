# Review and approve AWS changes

Start with a read so you can see what’s there. Before changing anything, show the user which account and resource will change, what will happen, what it could cost, and how you’ll check the result.

## Save a plan the user can approve

A write command previews the request by default and leaves `approval_ready: false`. To prepare a plan you can apply, use `--bind-aws --plan-out plan.json`. This checks the AWS identity and selects the service endpoint without sending the change. Generate a new plan with those flags if you saved it with an earlier version.

Review the original input alongside the plan because the saved plan hides secrets. Confirm the account, role, region, exact resource, settings and approval flags. For changes to access, public exposure, data movement, messages or spending, say what people and systems will be affected. Check whether AWS offers a snapshot, restore or other recovery for that action. Say when recovery would be manual or unavailable. Show the exact apply command and wait for approval.

## Apply the approved plan

Use the same input and pass `--plan-in plan.json --apply --yes`. The tool stops if the account, role, region, endpoint, request or required approvals changed. A fresh sign-in for the same IAM role can still use the plan. The configured account and region lists still apply.

- `--ack-no-snapshot` confirms the user understands that this write does not save a copy of the previous state.
- `--ack-irreversible` is required when the tool classifies the action as hard to undo.
- `--ack-spend-money` is required for covered actions that can add charges, including launching or starting EC2 instances, creating disks or capacity reservations, and certain RDS, EKS and Redshift changes. Review the expected cost of other changes too.
- `--output-file` gives the tool a private place to save a binary result.

## Check the receipt

Receipts normally live under `.state/runs/`. You can choose a path with `--receipt-out receipt.json`. Keep receipts, plans, run summaries and logs private.

| Receipt status | What to check |
| --- | --- |
| `limited` | The SDK returned a reply. Read the resource to check that AWS made the intended change. |
| `pending` | AWS is still working. Read the operation or resource before reporting completion. |
| `outcome_unknown` | A reply was lost or the result is unclear. Check the resource or AWS operation history before retrying. |
| `rejected` | AWS returned a client error. Check the error and the resource before deciding what to do. |

Compare the result with the approved plan. Check the important fields, any extra changes and any snapshot or earlier state you saved. For example, read a security group after a rule change or check bucket policy and public access after changing sharing. The tool records when no resource read-back ran. If repair or recovery needs a write, prepare a new plan and get approval.

## Repeat work

Run each command in its own process. Keep the account, region and exact targets visible when repeating a read in several regions or reviewing several resources. Review each group of changes before applying it. Stop on an unexpected refusal, access error or unclear result and check what happened. The tool has no separate batch worker.
