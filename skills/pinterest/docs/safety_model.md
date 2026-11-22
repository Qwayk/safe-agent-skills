# Approval and recovery

Start with a read or a preview. Before a board, section, or pin change, use `--plan-out` to save the preview for the signed-in account. Review the account, target, fields, and any difference you asked the tool to allow.

Apply the same command with `--apply --yes --ack-no-snapshot --plan-in FILE`. Deleting also needs `--ack-irreversible`. The tool checks the account and the exact plan before sending the change. For commands that look up what already exists, a changed target or request needs a new preview. See the [quickstart](quickstart.md) for a pin example.

For a group of pin-link edits, build the candidate list with `pins links plan --out FILE`. Use `--plan-out REVIEW.json pins links apply --plan FILE` to check the current links and save the preview for approval. Apply with the same candidate file and options plus the usual flags and `--plan-in REVIEW.json`.

The tool can read what was saved after a change. It cannot restore deleted boards or pins. `--ack-no-snapshot` records permission to proceed without a saved copy the tool could restore. If a create request has an unclear result, check Pinterest before sending it again. Board and pin commands send each change once per attempt.

The account inventory writes JSON files to your machine. Sign-ins and token imports can change local token files and need `--yes --ack-no-snapshot`. For ads, catalogs, reports, and jobs, use the [command reference](command_reference.md) for existing approval flags, including `--ack-spend` and `--ack-volume` where they apply.
