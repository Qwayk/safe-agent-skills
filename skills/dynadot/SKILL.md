---
name: dynadot-api-safe-cli
description: Run the Dynadot Qwayk CLI safely (dry-run first; no-snapshot approval for writes without saved before-state).
---

This page is the agent-facing rule sheet for the public Dynadot skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for the `dynadot-api-tool` command.

## Core rules (do not break)

- Default to **read-only**.
- Never ask the user to paste secrets into chat.
- Never print secrets (especially anything that could include the API key in a URL).
- For any domain transfer / bulk action: run a dry-run preview first, then apply only after explicit approval.
- For domain push / accept / decline: require `--apply --yes --plan-in`.
- If something is ambiguous (wrong domain list, wrong receiver username, unclear action), stop and ask a short clarifying question.
- For any API3 write command under `api3/`: run a dry-run first and require `--apply --yes --plan-in` (and `--ack-irreversible` for monetary/irreversible actions).
- Write apply needs a reviewed plan and `--ack-no-snapshot` before Dynadot HTTP when no before-state can be saved.
- For any write plan, read `before_state` as the live gate: `required: true`, `supported: false`, `status: no_snapshot_available`.
- For any write plan, read `recovery` as the no-recovery contract: Dynadot writes in this CLI are currently `irreversible_and_clearly_labeled`, with `backups: []`, `snapshots: []`, and `rollback_plan: null`.

## Safety workflow (always)

1) Connection check (read-only): `dynadot-api-tool --output json auth check`.
2) If the user requests a change:
   - Run the dry-run preview (no `--apply`) and show the plan summary.
   - Ask for explicit approval to re-run with `--apply --yes`.
   - After an approved apply attempt, confirm the receipt, verification result, or exact refusal reason.

## Command examples (placeholders only)

Connection:
- `dynadot-api-tool --output json auth check`

Inventory exports (read-only):
- `dynadot-api-tool --output json domains list --page 1 --out "<EXPORT_PATH>"`
- `dynadot-api-tool --output json domains info --domains-file "<FILE_WITH_DOMAINS>" --out "<EXPORT_PATH>"`
- `dynadot-api-tool --output json domains status --domains-file "<FILE_WITH_DOMAINS>" --out "<EXPORT_PATH>"`
- `dynadot-api-tool --output json domains folders list --out "<EXPORT_PATH>"`

Account reads (read-only):
- `dynadot-api-tool --output json account info [--out "<EXPORT_PATH>"]`
- `dynadot-api-tool --output json account balance [--out "<EXPORT_PATH>"]`
- `dynadot-api-tool --output json account coupons --coupon-type {registration,renewal,transfer} [--out "<EXPORT_PATH>"]`

Pricing reads (read-only):
- `dynadot-api-tool --output json pricing tld-price [--currency {USD,EUR,CNY}] [--page N] [--page-size N] [--out "<EXPORT_PATH>"]`

Domain search (read-only):
- `dynadot-api-tool --output json domains search --domain "example.com" [--domain "other.com" ...] [--show-price] [--currency {USD,EUR,CNY}] [--out "<EXPORT_PATH>"]`

Push domains (sender side):
- `dynadot-api-tool --output json domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE_WITH_DOMAINS>"`
- `dynadot-api-tool --output json --apply --yes --plan-in "<PLAN_FILE>" domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE_WITH_DOMAINS>" [--max-batches N] [--sleep-between-batches-s S]`

Push requests (receiver side):
- `dynadot-api-tool --output json domains push-requests list`
- `dynadot-api-tool --output json --apply --yes --plan-in "<PLAN_FILE>" domains push-requests accept --domains-file "<FILE_WITH_DOMAINS>"`
- `dynadot-api-tool --output json --apply --yes --plan-in "<PLAN_FILE>" domains push-requests decline --domains-file "<FILE_WITH_DOMAINS>"`

Transfer (guided end-to-end):
- `dynadot-api-tool --output json --plan-out "<PLAN_FILE>" --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"`
- `dynadot-api-tool --output json --apply --yes --plan-in "<PLAN_FILE>" --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"`

Name servers (audit + bulk set):
- `dynadot-api-tool --output json domains name-servers export --domains-export-in "<DOMAINS_LIST_EXPORT_JSON>" --out "<EXPORT_PATH>"`
- `dynadot-api-tool --output json domains name-servers diff --current-in "<EXPORT_PATH>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net" --out "<DIFF_PATH>"`
- `dynadot-api-tool --output json --plan-out "<PLAN_FILE>" domains name-servers set --diff-in "<DIFF_PATH>" [--max-domains N] [--max-batches N] [--sleep-between-batches-s S]`
- `dynadot-api-tool --output json --apply --yes --plan-in "<PLAN_FILE>" domains name-servers set --diff-in "<DIFF_PATH>" [--max-domains N] [--max-batches N] [--sleep-between-batches-s S]`

API3 (all official commands; safe-by-default):
- Discover commands: `dynadot-api-tool api3 --help`
- Example plan: `dynadot-api-tool --output json --plan-out "<PLAN_FILE>" api3 register --domain "example.com" --duration 1 --currency USD`
