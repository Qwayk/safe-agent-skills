# Safety model

The tool starts in read mode. It can look up account state and report what it sees.

## What the agent can do right away

- Check connection
- Read pricing, accounts, domains, DNS, SSL, marketplace listings, webhooks, and readback docs
- Prepare command plans for write actions

## What waits for your approval

The tool will not apply write commands without `--apply`.

High-risk writes also need `--yes` plus the matching acknowledgement flag:

- `--ack-spend`: registration, renewal, transfer
- `--ack-terms`: registration terms acceptance
- `--ack-destructive`: deletions
- `--ack-secret`: secret-bearing reads and writes, plus email password changes
- `--ack-send`: account invitations, webhook test delivery, and webhook resend
- `--ack-no-snapshot`: when no reliable before-state is available

Some write commands also ask for a native dry-run check before apply when the API supports it.

## Approval flow for live changes

1. The command runs in draft mode and returns a plan.
2. The tool signs the complete plan with a local HMAC key stored at `.state/plan-signing.key`.
3. You review command target, risk, and scope.
4. Apply verifies the signature before trusting the operation, target, inputs, expiry, idempotency key, snapshot state, or cost.
5. The tool rebuilds static acknowledgement requirements from the current operation metadata.
6. If approved, run with `--apply` and the required acknowledgements.
7. The tool attempts safe verification after write when a readback endpoint exists.
8. A receipt is written for review.

The signing key is local to the working directory. Keep the same `.state` directory for plan and apply. Copying only the plan to another machine or directory is not enough to authorize it. First-use key creation is create-if-absent: concurrent plan creators share the single winning 32-byte key instead of replacing one another's key.

For billable writes, the planned cost and a fresh apply-time cost must both have a valid matching cost signature. Missing, malformed, or changed cost fails closed before the live write.

## Secret output

Operations can return API credentials, invite tokens, webhook secrets, or SSL material.
These values are redacted from normal output.
For secret-bearing reads or writes, use both `--ack-secret` and `--secret-out`. The tool reserves and checks the destination before any provider request, then atomically stores the full result with `0600` permissions. Invalid, unwritable, directory, and symbolic-link destinations are refused without calling Porkbun.

Tool-owned `.state` directories use `0700`. The signing key, plans, receipts, onboarding env file, and secret result files use `0600` and same-directory atomic replacement, so a partially written file is never treated as complete.

Plan, receipt, and secret output roles must be different from one another. They also must not alias the environment file, JSON input file, or plan input file. The check covers computed defaults, explicit paths, relative and absolute spellings, `..`, symbolic links, and existing files that share the same identity. A collision is refused before any provider request or destructive local replacement.

The invite token for `porkbun account get-account-invite-status` must be supplied through a JSON `--input` file. It is not accepted as `--token`, which keeps it out of shell history and process arguments.

## Transport and output privacy

Production requests use only Porkbun's two official v3 hosts. Redirect following is disabled, and every `3xx` response fails before a read, write, or receipt can be marked successful.

Configured API credentials and sensitive request values are removed from normal results and from validation, provider, transport, readback, and unexpected error output. Useful non-secret error codes and request IDs remain available.

## No rollback promise

The tool does not promise automatic rollback unless a command path is explicitly reversible.

## Why this is not all-or-nothing

Safe reads happen first so the user can understand what is at risk before any live change.
