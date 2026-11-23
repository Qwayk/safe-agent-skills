# Approvals and receipts

List models, files, and jobs or count tokens when that fits the task. Ask for approval before sending requests that can cost money, including generation, streaming, embeddings and predictions. Use `--ack-spend-money` once the request is approved. The flag records the approval in the command. Google sets the prices and handles billing. [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)

## Review a change

Create a dry-run plan for uploads, deletes, permissions, cache changes, and changes to batches, file search or tuned models. Starting a batch generation job or an asynchronous batch embedding job also needs a plan. Review the model or resource, the request file and any media file. Check the impact, whether there is a copy you can restore, and what you’ll check afterward. Keep the request file so you can review the original text. The saved plan shows a fingerprint of the request body and upload bytes.

Once approved, use `--apply --yes --plan-in plan.json` with the same settings folder and API key. Add `--ack-no-snapshot` if Gemini has no copy to restore, `--ack-irreversible` where required, and `--ack-spend-money` for actions that can charge, such as starting a batch, creating or extending a cache, or indexing a file. Generate and review a new plan if the input changed or the plan predates these checks.

## Check the result

The tool saves a receipt in the run folder or at the path you give with `--receipt-out`. Check the operation, target and what Gemini returned. Read the resource back where possible. If the reply is missing, the receipt says the outcome is unknown. Check Gemini before making a new plan. A plan can be sent once, even when the reply was lost.

Keep request files, plans and receipts private if they contain account details or generated content. Routine run logs show the command name without its request text. Scope any rollback to what the service actually lets you undo and get approval before sending it.
