# Review an OpenAI change

OpenAI requests stay on your machine until you add `--live`. Before sending a change or a request that can cost money, save a plan and show it to the person who can approve it. Check the account and project, exact input or file, cost, and any changes that could be difficult to undo.

## Save and approve the plan

Prepare the plan with `--plan-out`. Apply with `--live --apply --plan-in <file>` and the same request inputs. The tool checks the API key, organization, project, settings folder, inputs, and uploaded file contents against the saved plan. After a key, account, or upload changes, prepare a new plan for review. Plans saved before the November update also need to be prepared again.

Use `--ack-no-snapshot` to confirm that the tool cannot save the live state before applying. It cannot restore that state for you. Add `--yes --ack-spend-money` for actions that can start billable work or add billable storage, such as creating a response or starting a batch. Add `--yes --ack-irreversible` for deletes. A read such as `getResponse` and the free moderation endpoint do not need the spending flags. Moderation still has a saved plan because it sends input to OpenAI. [OpenAI pricing](https://developers.openai.com/api/docs/pricing) · [Command examples](command_reference.md)

## Check what happened

The tool saves a private receipt under `.state/receipts/` beside the settings file before it sends a write. That approval can send once. `--receipt-out` saves a second copy if needed.

After a reply, look for the resource ID and its status. The tool reads back that specific resource where it has a documented way to check it. A receipt marked `response_only` gives the provider’s reply. A receipt marked `pending` or `needs_check` needs a check in your account before you prepare another request. For a batch or another job that runs in the background, use its ID to check progress.

Keep plans, receipts, and binary or streaming files private. The tool saves binary and streaming replies in the run folder when needed. The receipt gives the file path and a checksum. Routine run logs show the command name without the original prompt or options. [Local run history](command_reference.md#run-history) · [Sample receipt](examples/receipt.example.json)
