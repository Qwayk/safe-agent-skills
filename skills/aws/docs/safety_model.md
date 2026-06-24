# Safety model

AWS safety starts with knowing the target. This tool looks at the account and region first, asks for review before risky changes, and records what it could prove afterward.

That matters because AWS mistakes can create access, expose data, move data, send messages, delete resources, or increase spend.

A good safety ask is: "Check the AWS identity and region first, show me the plan for any change, and only run the change after I approve the reviewed plan and any no-snapshot or irreversible risk."

## What safe use looks like

- `auth check` proves the caller with STS `GetCallerIdentity`.
- Account and region allowlists can block the wrong target before non-STS service calls.
- Reads run directly when the caller has permission.
- Writes start as dry-run plans.
- Live writes need `--apply`, `--plan-in`, and `--yes`.
- Generated AWS writes are treated as no-snapshot unless an operation-specific read-back is added later, so live writes normally need `--ack-no-snapshot`.
- Delete-like and hard-to-undo operations need `--ack-irreversible`.
- Receipts include a verification section. A response from AWS without resource read-back is recorded as `limited`, not `verified`.
- Plans, receipts, logs, and run history are redacted.

## AWS risk categories

The tool classifies each pinned operation conservatively. These categories help a reviewer know what to slow down:

- `security_identity`: IAM, roles, policies, credentials, SSO, KMS, or permission-related changes.
- `secret`: secrets, keys, tokens, certificates, or credential-like material.
- `spend_quota`: billing, quotas, capacity, compute, marketplace, or usage-related changes.
- `public_exposure`: public access, DNS, CDN, firewall, route, or sharing changes.
- `data_movement`: imports, exports, replication, streams, transfers, backups, or downloads.
- `messaging`: email, SMS, notifications, queues, topics, or publish/send actions.
- `no_snapshot`: no generic safe before-state or read-back is available.
- `unknown_mutating`: the model suggests mutation, but the generic path cannot classify it more narrowly.
- `irreversible`: delete-like or hard-to-undo actions.

## What the flags mean

- `--plan-out` saves the dry-run plan.
- `--plan-in` loads the reviewed plan for live apply.
- `--receipt-out` saves the apply receipt.
- `--ack-no-snapshot` says the action cannot save a reliable before-state or generic read-back.
- `--ack-irreversible` says the action is hard to undo.
- `--output-file` is required when an AWS response returns binary data.

## Normal change flow

1. Check identity.
2. Build a dry-run plan.
3. Review the account, region, service, operation, input, allowlists, and risk categories.
4. Apply only after clear approval.
5. Verify what the tool can verify. For the generated AWS surface, this means the tool checks the reviewed plan, confirms the SDK call returned, records the response status when present, and says if no resource read-back was possible.
6. Save the receipt and local run summary.

## What the tool refuses

- A live write without `--apply`.
- A live write without `--plan-in` or `--yes`.
- A reviewed plan that no longer matches the current service, operation, region, or input.
- A call blocked by account or region allowlists.
- A no-snapshot, unknown mutating, or irreversible write without the matching acknowledgement flags.
- A binary response without `--output-file`.

## Run history

For write-capable commands, the tool keeps a local run folder under `.state/runs/` and appends a row to `.state/runs/index.jsonl`.

That history helps answer simple questions later: what was planned, what ran, which AWS target was used, and whether verification was full, limited, or failed.
