# Review and check Instagram changes

Preview an action before changing posts, comments, messages, or token settings. Review the account, target and exact request. Use `--apply --ack-no-snapshot` after approval to proceed without a saved copy of the previous state. Publishing, sending messages and deleting comments also need `--yes`. Deleting comments needs `--ack-irreversible`. The tool has no automatic restore command.

Save a plan with `--plan-out` when preparing a draft or publishing it. Use the same request and `--plan-in` to apply it. The command checks the account before sending it to Instagram. Save a new plan and get it reviewed if the account, media, caption, draft ID or Graph API settings change. [Publishing example](quickstart.md#review-and-publish-an-image)

The receipt contains Instagram’s reply. After publishing, the tool reads the post by the ID Instagram returns and records whether that separate read confirmed it. If an answer is unclear, check the draft status before sending again. [Publishing help](troubleshooting.md#publishing)

For a group of changes, read the targets first and make a preview for each change. Send only the ones the user approved. Save a receipt with `--receipt-out` or look up the local plan, refusal or receipt with `runs list` and `runs show`. The run files live under `.state/runs/` next to your settings file. Keep private account details and credentials out of anything you share.
