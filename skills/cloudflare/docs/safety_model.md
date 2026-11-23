# Approvals and private results

Start by finding the right Cloudflare account, zone or resource. Ordinary reads can run within the task you approved. A command that changes Cloudflare starts with a plan. Review the plan and approve the exact change before the agent sends it.

## Review the plan before a change

Check the target and the settings the agent will change. Ask it to show what the tool can save before the change and how it will check the result afterward. If the target, connection, or saved request changes after review, ask for a fresh plan. Keep tokens and private result files out of the review message.

- To save a plan for review, use `--plan-out <FILE>`. Use `--plan-in <FILE>` for commands that support applying a saved plan.
- Cloudflare writes require `--apply --yes`. Where the CLI can read and save the old settings safely, review the saved copy. The plan or receipt can refer to it in `before_state` or `before_state_path`.
- If the command cannot save the old settings and offers `--ack-no-snapshot`, explain what would have to be recovered by hand. Use the flag only when the user explicitly approves continuing without that saved copy. A failed safety check or unclear target still stops the work.
- Actions that cannot be undone and certain operations that return a secret need `--ack-irreversible`. Applied `operations` writes under `/accounts` also require a file path with `--out`. Deletes under `/accounts` require the extra acknowledgement. The [command guide](command_reference.md) lists the flags for each command.

For DNS, check the existing record and the new values. The tool reads the record again after applying. For a Worker deployment, show each version and its share of traffic. The tool checks those values in the deployment Cloudflare returns.

For Pages, check the project’s production branch first. Pass it with `--production-branch` when it differs from `main`. The saved plan records the branch and files, including changes to headers and redirects. Apply checks the actual production branch before uploading. A deployment without saved old state requires `--ack-no-snapshot`. Use `--out` to save the private result.

Save a new plan for a DNS, Worker, Pages, or `operations` write if the saved plan predates these checks. Before onboarding domains in bulk, run `auth zone-create-check` for the intended account.

## Keep private results in files

For private reads such as Worker code, KV values, logs, account member details and Email Routing results, use `--apply --out <FILE>`. Put the file under `--project-dir`. The agent should summarize what matters and tell you where it saved the file. Keep the contents out of chat and Git. For Worker tails, keep the secret WebSocket URL in memory and save only the events to the file.

Some reads send a POST request. Browser Run quick actions, KV bulk get and Queue pull use `--apply --out <FILE>` for this reason. Browser Run accepts `--yes` as well, but it is optional. Follow the [command guide](command_reference.md) for commands with additional requirements.

## Check the result and keep the receipt

Compare the receipt with the approved plan. Check which settings changed, which checks passed and which results are still uncertain. Where Cloudflare supplies a matching read, the tool can check the result by reading the resource again. A successful API response on its own does not verify the setting you wanted.

Use `--receipt-out <FILE>` for commands that support it. Run records usually live under `.state/runs/` beside the selected env file. Use `runs list` or `runs show` to find the earlier run. Keep these records private.

If Cloudflare returns a server error or the reply is lost, the tool keeps a receipt marked `outcome_unknown`. Check the resource or deployment before trying again. The general `operations` commands provide no automatic undo. If a receipt includes `rollback_plan`, it describes a recovery you can review and carry out manually. Ask for approval before changing anything to recover.
