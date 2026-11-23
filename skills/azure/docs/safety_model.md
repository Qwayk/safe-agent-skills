# Review and approve Azure changes

Before changing anything, show the user the tenant, subscription and exact resource, what will change, what it could cost, and how you’ll check the result. Read the target first when you have permission.

## Save a plan the user can approve

A write command shows an offline preview by default. It says `approval_ready: false`. To save a plan you can apply, use `--bind-azure --plan-out plan.json`. This checks the current connection and records the endpoint and exact request without sending the change. Save older previews again with those flags before asking for approval.

Review the original input alongside the saved plan, which hides private values. Check the exact target and what the change could affect, including access, public networking, costs and data. If Azure offers a snapshot or a way to undo this change, explain it. Say when recovery would need a manual step or is unavailable. Show the exact command and wait for approval.

## Apply the approved change

Pass `--apply --yes --plan-in plan.json` with the same input file. The tool checks the current operation and the approved identity, subscription, endpoint and request. A changed plan needs another review. When the tool uses a manually supplied token, replacing that token also requires a new plan.

- Use `--ack-no-snapshot` when the command cannot save the previous state or the operation requires it.
- Use `--ack-irreversible` when the tool classifies the action as hard to undo.
- Use `--ack-spend-money` for covered actions such as starting a VM or creating a VM, disk or managed Kubernetes cluster. Review expected costs for other changes as well.

The configured tenant, subscription, resource group, location and service limits still apply. Azure permissions determine what the sign-in can do.

## Check the receipt

Use `--receipt-out` to pick a file, or find the receipt in the local run folder. Keep plans and logs private. Status checks use the same Azure host as the approved request. If Azure asks you to wait, the receipt shows when to check again.

| Status | What to do |
|---|---|
| `limited_verification` | Azure returned a reply. Read the resource to confirm the exact change. |
| `pending` | Azure is still working or asked you to wait. Check the operation or resource before reporting completion. |
| `operation_failed` or `rejected` | Azure reported a failure or rejected the request. Read the error and check the resource before deciding what to do next. |
| `outcome_unknown` | The write or its status check lost a reply. Check Azure’s operation history or the resource before trying again. |

Compare the resulting fields with what the user approved. If a fix or rollback needs another write, prepare a fresh plan and ask for approval. [Microsoft’s guide to Azure status checks](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations)
