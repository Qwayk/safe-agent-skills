# Review and check Threads changes

An API write starts with a preview. Check the account, target, exact request and what can be recovered. Use `--plan-out` to save the preview. Send a change only after approval, with `--apply` and `--ack-no-snapshot`. That second flag approves proceeding without a saved copy of the previous state. A delete also needs `--yes --ack-irreversible`. The tool has no automatic restore command.

Creating a draft and publishing it both require the matching saved plan with `--plan-in`. The tool checks the request and the signed-in account before sending. If the text, account, draft ID or API settings change, save a new plan and get it reviewed. [Posting example](quickstart.md#review-and-publish-a-post)

The receipt shows what Threads returned. Publishing also reads the post by the returned ID and records whether that read confirmed it. A missing ID or a failed read leaves confirmation open. Check the draft status before repeating a request with an unclear result. [Publishing help](troubleshooting.md#publishing)

Use `--receipt-out` to save the reply or `runs list` and `runs show` to inspect local run records. Keep settings, tokens and private post details out of anything you share.
