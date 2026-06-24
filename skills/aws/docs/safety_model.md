# Safety model

AWS changes are safer when the tool checks identity first, writes a plan second, and keeps a receipt last. That matters because a single AWS action can change access, public exposure, compute state, data movement, messaging, secrets, quotas, or spend. The skill is built to make the account, region, action, input, and risk visible before anything live is sent.

A good safety ask is: "Before planning this AWS change, tell me the account, region, operation, risk category, required approvals, and whether the receipt can verify the result with a read-back."

## What safe use looks like

- `auth check` proves the caller with STS `GetCallerIdentity`.
- Allowlists can block the wrong account or region before a live call.
- Reads run directly.
- Writes start as dry-run plans.
- Live writes need `--apply`, `--plan-in`, and `--yes`.
- Generated AWS writes are treated as no-snapshot unless an operation-specific read-back is added later, so live writes normally need `--ack-no-snapshot`.
- Irreversible writes need `--ack-irreversible`.
- Receipts include a verification section. That section says what was checked and clearly says when no safe read-back was available. A 2xx AWS SDK response without read-back is recorded as `limited`, not `verified`.
- Plans, receipts, logs, and run history are redacted.

## What the flags mean

- `--plan-out` saves the dry-run plan.
- `--plan-in` loads the reviewed plan for a live apply.
- `--receipt-out` saves the apply receipt.
- `--ack-no-snapshot` says the action cannot save a before-state or generic safe read-back.
- `--ack-irreversible` says the action is hard to undo.
- `--output-file` is required when the AWS response returns binary data.

## Normal change flow

1. Check identity.
2. Build a dry-run plan.
3. Review the service, operation, region, allowlists, risk, and input.
4. Apply only after clear approval.
5. Verify the result. For the generated AWS surface, this means the tool checks the reviewed plan, confirms the SDK call returned, records the response status when present, and says if no resource read-back was possible. If no read-back ran, the receipt stays `limited`.
6. Save the receipt and local run summary.

## What the tool refuses

- The tool refuses when `--apply` is missing for a write.
- The tool refuses when `--plan-in` or `--yes` is missing for a live write.
- The tool refuses when the reviewed plan no longer matches the current service, operation, region, or input.
- The tool refuses when allowlists do not match the current AWS identity.
- The tool refuses high-risk, no-snapshot, unknown mutating, or irreversible writes until the matching acknowledgement flags are present.

## Run history

For write-capable commands, the tool keeps a local run folder under `.state/runs/` and appends a row to `.state/runs/index.jsonl`.

That history helps answer simple questions later, like what changed last time and whether verification was full, limited, or failed.
