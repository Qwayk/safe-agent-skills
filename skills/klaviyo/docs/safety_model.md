# Review a plan and receipt

Run the command without `--live` or `--apply` to see what it would do. A read can use `--live` once you’ve confirmed the intended account and records.

## Before a change

Save the preview with `--plan-out plan.json`. Review the account, record IDs, request and any attached files. For a list change, check whether the request adds people to a list or also changes what they agreed to receive. For a flow change, check which flow or action will change status.

After approval, use the same settings and inputs. Writes need `--live --apply --ack-no-snapshot`. The last flag confirms approval to proceed without a saved copy of the previous state. If you provide `--plan-in`, the tool checks the request and file contents against the reviewed plan before sending.

Flow and flow-action status changes, bulk jobs, sends and cancellations, suppressions, removal and deletion, and other high-impact actions also require `--plan-in` and `--yes`. Make a new preview for a flow status change or attached file if the plan was saved before this update.

A result with `refused=true` means the tool stopped before sending a change. Read the reason before deciding what to do.

## After a change

Save the receipt and check `verification.status`.

- **Accepted.** Klaviyo has the job. Run the check in `verification.next_command` when the receipt includes one. For a bulk import, check failed rows as well as progress.
- **Response received.** Read the reply and then check the actual record. For a flow, use `api get_flow --path id=<flow-id>` with the same settings file and `--live`.
- **Rejected.** The provider returned an error. Check what it rejected before preparing another request.
- **Uncertain.** Check the account or job in Klaviyo before trying again. The first request may already have taken effect.

The tool saves plans and receipts under `.state/runs/` by default. It can also save to paths you choose. Keep those files private if they contain customer data. This tool leaves recovery to the person approving the change, so check what can be restored before you proceed. [Klaviyo bulk import results](https://developers.klaviyo.com/en/docs/use_klaviyos_bulk_profile_import_api)
