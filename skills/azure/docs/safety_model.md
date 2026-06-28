# Safety model

Safe Azure work should feel like look first, think second, and change last. Azure can control identity, networking, compute, storage, databases, secrets, quotas, and billing, so this skill treats reading and changing as separate jobs. The agent should first show what it found, then prepare a plan for any change, then wait for approval before applying it.

A good safety ask is:

```text
Use the Azure skill to inspect this subscription, point out anything that could affect access, spend, public exposure, or secrets, and stop before making any change.
```

## What safe use looks like

A safe run starts with a read, names the subscription or resource group, and explains whether the result looks expected. A change should be a second step, written as a plan that can be reviewed before the tool sends anything live.

## What it does well

- Read commands stay low friction and do not need extra apply flags.
- Write commands are always shown as planned output first.
- Live write flow requires explicit confirmation flags.
- Secret-like values are redacted in sensitive read results.
- Each run leaves a local record that can be checked after the work.

## Write gate

A live write is refused unless all conditions are met:

- `--plan-in` points to a plan file created from dry-run output
- `--apply` is set
- `--yes` is set
- classification risk check passes
- if risk class includes `no_snapshot`, `identity_security`, `spend_quota`, or `public_exposure`, `--ack-no-snapshot` is required
- if risk includes `irreversible`, `--ack-irreversible` is required

The tool returns a structured refusal instead of running when one of those requirements is missing.

## Read behavior

- Read operations can run when `AZURE_API_TOKEN` is set.
- `AZURE_DATA_PLANE_ENDPOINT` is required only for data-plane operations.
- The result is returned directly and marked as not dry-run.
- Secret/token/key/password/credential-like reads are classified as `sensitive_read`; response body values are redacted by default, including generic fields such as `value`.

## Readiness and evidence

Each run writes evidence fields in the output:
- `dry_run`
- `plan` or `receipt`
- run history row and artifacts path
- any refusal reason if the action is blocked

## Higher-risk handling

- Plan and receipt are stored and should be reviewed before a second step.
- Azure rollback is not automatic; plans and receipts are the primary audit records.
- Identity, public exposure, spend, quota, and irreversible actions should be reviewed with extra care.

## Important caveat

`auth check` and local dry-runs confirm command readiness and policy behavior.
It does not verify full live Azure behavior until valid credentials and a live target are available.
