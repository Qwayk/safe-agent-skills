# What happens before Asana changes

The agent can read Asana after it confirms the connection and exact target. Reads do not use the write approval flow, but sensitive results such as audit logs and completed exports should still be explained before they are shared or saved.

## Every write starts as a saved plan

Running a POST, PUT, or DELETE command without `--apply` cannot send that provider write. The tool instead saves a JSON plan with:

- the fixed operation and exact Asana path
- documented path and query parameters
- the JSON body or attachment file name, size, and SHA-256 hash
- risk reasons and required acknowledgements
- before-state from a same-target GET when the pinned API provides one
- a clear warning when no reliable before-state exists
- the available readback method
- an explicit statement that rollback is not promised

New plans use schema 2. The plan ID is still a readable content identity for approval, but it is not the security boundary. A random local HMAC-SHA256 key is stored outside the plan at `.state/plan-signing.key`, and the plan carries an authenticated signature. The key is never printed or copied into the plan.

## Apply needs approval of that exact plan

An apply must include `--plan-in`, `--apply`, and `--approve PLAN_ID`. Request parameters, bodies, and file paths cannot be repeated on the apply command because the reviewed plan is the only source.

Before any snapshot read or provider request, apply verifies the local signature. It then selects the fixed operation again, reconstructs the path and typed query from the saved validated inputs, and revalidates the body, attachment metadata and hash, risk, snapshot identity, verification method, and rollback statement. Editing the method, path, query, body, files, operation, risk, snapshot, or verification data and recomputing the public plan ID still fails before HTTP. This also prevents a fixed command from being redirected to `/batch`, SCIM, or another operation.

The signing key belongs to the local state beside the selected env file. A missing or changed key, an unsigned plan, or an older schema-1 plan is refused; create and review a new plan.

If the plan has a before-state, the tool reads the target again and refuses when it changed after planning. If the operation has no reliable before-state, apply also needs `--acknowledge-no-snapshot`.

## Changes that need stronger approval

The inventory marks deletes and operations involving access, roles, memberships, permissions, teams, workspace administration, visible collaboration, attachments, webhooks, broad exports, rules, agents, budgets, rates, approvals, automation, duplication, or other wider effects. These plans require `--acknowledge-risk` during apply.

The request body can also raise an ordinary command to stronger approval. Multiple targets or values are treated as bulk or fan-out work, and fields such as assignees, followers, members, or approval status are treated as visible collaboration, notification, or approval effects.

This extra flag does not replace review of the target and request. It records that the user accepted the named higher-risk reasons.

## Verification and receipts

After a successful PUT, the tool uses a documented same-target GET when available and compares the requested fields. After a DELETE, it checks for a not-found response when the same-target read exists. Other operations record honestly that the provider accepted the request but no reliable same-target verification exists.

Every apply attempt saves a receipt, including provider failures. A receipt records the plan ID, command, provider status, request ID when present, asynchronous state, verification result, and the provider result with secret-like fields removed.

New plans, receipts, signing keys, and optional audit logs are written atomically with owner-only mode `0600`. State directories created by the tool use mode `0700`. Replacing an existing file never broadens its current permissions.

## Asynchronous work

Exports, duplication, template instantiation, and other operations may return before the work finishes. The tool distinguishes accepted, queued or running, succeeded, failed, timed out, and unverified states. `--wait` polls the fixed Asana job endpoint only when the response includes a job GID. It never treats request creation alone as completed work.

## Files, output, and secrets

Attachment files are sent only by the fixed attachment command. The plan stores file metadata and apply refuses if the file hash changed. Unexpected binary output must be saved with `--download-to`; it is never dumped into JSON stdout.

The bearer token is read from `ASANA_ACCESS_TOKEN`. It is not placed in plans, receipts, logs, errors, examples, or normal output. JSON mode emits exactly one JSON object.

## No arbitrary escape path

The CLI never accepts a URL, HTTP method, relative API path, SDK call, or raw batch entry. `POST /batch` is intentionally excluded because it would bypass the fixed operation boundary. App Components and SCIM are separate and unsupported.
