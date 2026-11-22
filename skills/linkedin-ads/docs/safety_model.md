# Approve and check a LinkedIn Ads change

Read the current account and affected item first when that helps you choose the change. Reads can contact LinkedIn directly. Some previews use an HTTP `POST` even though they leave the ad account unchanged.

## Review the plan

Run the change command with `--plan-out plan.json` and without `--apply`. Check the account, IDs, request details, and approval requirements in the saved plan. Confirm that the plan has the whole change you intended and that it contains no credentials.

Before any live change, get the user's approval for the exact change and for proceeding without a saved copy of the old settings. Every write needs `--apply --ack-irreversible --ack-no-snapshot`. Delete, batch, and permission-changing commands also need `--yes --plan-in plan.json`. The tool checks that the saved plan matches the request for those higher-risk commands.

The plan records `before_state.required: true` and `before_state.supported: false` for writes. There is no automatic restore for those changes.

## Read the result

Read the JSON result before reporting what happened. If it says `refused: true`, use the stated reason to explain what stopped. These refusals can exit with code zero because the tool stopped safely before sending the change.

A receipt from `--receipt-out` records LinkedIn's response. Its `changed` and `verification.ok` fields are `null` when the tool only checked the HTTP reply. To confirm a campaign change, read it again with `ad-campaigns get` using the same account and campaign IDs, then compare the field you changed. If the reply is lost or the new state is unclear, check LinkedIn before deciding whether to send another write.

LinkedIn still checks the app's access, token permissions, and member role. See the [coverage table](api_coverage.md) for the meaning of each access label.
