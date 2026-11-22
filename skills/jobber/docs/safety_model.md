# Review a Jobber change

Start by checking the account and target record. Save the preview with `--plan-out` so you can review the exact operation and values.

## Apply an approved plan

- Apply with `--apply --yes --plan-in <reviewed-plan.json>`. Use a reviewed plan for CSV jobs that include writes as well.
- Plans and receipts report `snapshot_status: "No snapshot available"`. For a high-risk change, review the recovery notes before adding `--ack-no-snapshot`. For a clearly irreversible change, add `--ack-irreversible` after approving that action.
- The tool saves Jobber's reply with `--receipt-out`. Check the reply for errors and read the target record again where possible. There is no automatic undo.
- If the result is unclear, inspect the record before repeating the change. Review any recovery action separately.

See the [command guide](command_reference.md) for exact flags and [the setup guide](onboarding.md) for private account settings. Keep tokens, app secrets and OAuth state out of logs and shared files.
