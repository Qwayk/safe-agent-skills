# Safety model

AWS safety starts with a simple rule: the agent must know the account, role, and region before it does useful work. A good AWS answer should never leave you wondering which account was touched.

After that, the safest path is read first, plan second, apply last. That matters because an AWS mistake can create access, expose a bucket, open a network rule, move data, send messages, delete resources, or increase spend.

A good safety ask is: "Show me the AWS account, role, and region first. Read the target resource if possible. If a change is needed, show the plan and the extra approval flags before anything runs."

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

The tool classifies each pinned operation conservatively. These labels are not there to sound technical; they tell the reviewer what kind of real-world harm to slow down for:

- `security_identity`: could affect IAM, roles, policies, credentials, SSO, KMS, or permissions.
- `secret`: could touch secrets, keys, tokens, certificates, or credential-like material.
- `spend_quota`: could affect billing, quotas, capacity, compute, marketplace, or usage.
- `public_exposure`: could affect public access, DNS, CDN, firewall, routes, sharing, or internet reachability.
- `data_movement`: could import, export, replicate, stream, transfer, back up, or download data.
- `messaging`: could send, publish, notify, queue, email, or text someone.
- `no_snapshot`: the generic AWS path cannot save a reliable before-state or read-back for this operation.
- `unknown_mutating`: the AWS model suggests mutation, but the generic path cannot classify the effect more narrowly.
- `irreversible`: delete-like or hard-to-undo.

## What the flags mean

- `--plan-out` saves the dry-run plan so a person can review it.
- `--plan-in` loads the reviewed plan for live apply.
- `--receipt-out` saves the apply receipt after a live attempt.
- `--ack-no-snapshot` says you understand the tool cannot save a reliable before-state or generic read-back for this operation.
- `--ack-irreversible` says you understand the action is delete-like or hard to undo.
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
