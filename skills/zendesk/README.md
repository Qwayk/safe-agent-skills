# Zendesk

**Capability:** Reads + careful changes

Zendesk is where support tickets, users, organizations, tags, views, and workflows hold sensitive customer conversations that teams rely on every day.

This skill helps an agent inspect Zendesk Ticketing data, validate the pinned API inventory, review sensitive support records carefully, and prepare change plans before anything touches live support data.

Use it for questions like: "How many tickets match these rules?", "Which users or organizations are tied to this issue?", "Can you validate the command inventory?", "Can you preview this metadata cleanup?", or "Will this output include customer details?"

Zendesk outputs can include names, emails, phone numbers, addresses, ticket bodies, and internal notes. Live reads need `--live`; API writes start as dry-run plans and need explicit no-snapshot approval when useful before-state cannot be saved first.

A good first ask is: "Check the Zendesk connection, show the safest ticket and user read options, count tickets that match my rules, and stop before any changes."

## Start here first

- Want ideas for real Zendesk work? [What you can do with Zendesk](docs/use_cases.md)
- Need setup? [Connect your Zendesk account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check auth readiness and confirm the pinned Zendesk command inventory is valid.
- Search, count, and inspect tickets, users, organizations, tags, views, and other Ticketing API records with exact commands.
- Review planned ticket or metadata changes before anything goes live.
- Plan batch changes from CSV with the same review-first safety pattern.
- Keep proof of what ran through saved plans, refusals, receipts, and local run history.
- Handle Zendesk data carefully when outputs may include names, emails, ticket bodies, or other customer details.

## What access this skill needs

- Your Zendesk subdomain or base URL.
- Your Zendesk email plus API token for the simplest setup, or an OAuth bearer token if your team uses OAuth.
- Enough Zendesk permissions for the records and actions you want to review or change.
- A private local workspace, because outputs can include sensitive support data.

## Install and first run

Install slug: `zendesk`

Ask your agent to install the `zendesk` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@zendesk -g -y
```

Then try a safe first ask like:

```text
Check the Zendesk connection, show the safest ticket and user read options, count tickets that match my rules, and stop before any changes.
```

## How this skill stays safe

- Offline plans are the default.
- Live reads need explicit `--live`.
- Zendesk outputs may include ticket bodies, names, emails, phone numbers, or other customer data, so saved artifacts should be treated as sensitive.
- API writes need explicit review first. When there is no saved before-state, they also need explicit no-snapshot approval before Zendesk HTTP.
- Delete-style actions also need `--ack-irreversible`.
- Demo writes and some jobs write rows still refuse honestly instead of pretending to perform live Zendesk changes.
- The pinned OpenAPI snapshot, command inventory, docs, tests, and proof files all live in this repo so you can inspect the exact surface the agent is using.

## What it covers today

This skill covers:

- auth checks, token status, and local inventory validation
- explicit `api <operation>` commands for the pinned Zendesk Ticketing API surface
- live reads when you add `--live`
- careful API write planning before Zendesk HTTP
- jobs, demo safety flows, and local run history

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target records, payload, sensitive-data risk, and permissions before apply.
- Read-only calls can run live with `--live`.
- Write plans should tell you the exact live flags needed for the action.
- When there is no saved before-state, write attempts need explicit no-snapshot approval.
- Delete-style actions also need irreversible acknowledgement.
- Demo write and some jobs write surfaces may still stop at an honest refusal instead of sending live Zendesk writes.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- API apply paths can save receipts with `--receipt-out` when the command supports it.
- Safe refusals prove when nothing changed.
- Local run history can be reviewed under `.state/runs/`.
- The proof pack includes redacted version, auth, plan, and receipt examples.

## Limits

- This tool is intentionally strict about writes when useful before-state is missing.
- Some demo and jobs write surfaces are still stub-only and refuse honestly.
- Zendesk data can be sensitive, so even safe reads still need careful handling and storage.
- Recovery is explicit only; do not assume automatic rollback, backup, or snapshot support unless the plan says it exists.

## Helpful docs

- [Browse all Zendesk docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
