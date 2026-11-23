# Approve and check changes

You can read a file, look up comments, or get image links before deciding what to change. For a write, the tool shows a preview and waits for your approval.

## Before sending a change

1. Use the Figma connection and file or team you intend to change. Run the command with `--plan-out PATH` to save the preview.
2. Review the exact target and change. For a comment, check the file, the thread if it is a reply, and the full text.
3. Review what you can undo. The current commands save no before-state to restore. Apply needs `--ack-no-snapshot` after you approve that limit. Commands marked irreversible also need `--ack-irreversible`.
4. After approval, run the same command with `--plan-in PATH --apply --yes` and the required acknowledgements. Use `--receipt-out PATH` to pick where to save the result.

The plan must match the request and the Figma connection. Make a new preview if you change the connection, replace the token, change the request, or have a plan from an older version or from before setup. You can still preview without a token while planning the work.

## After sending a change

Read the result before reporting success. A refusal means the tool stopped before sending the change. Figma can accept a request even if the tool cannot check the result afterward. For comments, the tool checks the file's comment list when it can. Read access to comments is a separate Figma permission.

Check that the receipt matches the approved target and change. Note whether Figma accepted the change, what the tool could confirm with a follow-up read, and the saved record of approval to proceed without a copy of the previous state. If the result is unclear, inspect the current state before retrying. A second post can leave a duplicate comment.

Run `runs list` or `runs show --run-id ID` to find saved runs. Keep plans, receipts, comments, and image links private when they contain workspace information. Before sharing records, check for secrets such as webhook passcodes in request bodies.
