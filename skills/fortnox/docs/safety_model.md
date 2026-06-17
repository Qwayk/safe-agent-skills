# Safety model

Fortnox can affect invoices, supplier bills, bookkeeping, payroll, stock, file attachments, sends, bookings, and deletes. The safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong tenant, changing the wrong live record, sending a document too early, booking accounting work incorrectly, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the Fortnox record first, show me the plan for any change, and only run the change after I approve the reviewed plan and any no-snapshot or irreversible risk."

## Standard flow

1. Generate a dry-run plan.
2. Review the plan.
3. Apply with `--apply --yes --plan-in`.
4. Verify the change.
5. Keep the receipt.

## What the flags mean

- `--apply` turns a dry-run into a real change.
- `--yes` confirms the reviewed plan is the one you want to run.
- `--plan-in` reuses the saved plan you already reviewed.
- `--ack-no-snapshot` is required for high-risk applies when the tool has no useful before-state snapshot.
- `--ack-irreversible` is required for changes you cannot realistically undo.

## What gets refused

- Missing or unclear targets.
- Unsafe writes without the right review flags.
- `jobs run`. It stays unsupported until real registry-backed rows exist.
- Anything that would force the tool to guess.

## What proof you should expect

- A saved plan when you ask for one.
- A receipt after apply.
- A follow-up read or other verification that shows the change really landed.
