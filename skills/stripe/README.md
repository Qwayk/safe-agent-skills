# Stripe

**Capability:** Reads + careful changes

Stripe is where billing problems become real customer problems: subscriptions, invoices, refunds, payouts, transfers, disputes, products, prices, and connected accounts all live close to real money.

This skill helps an agent inspect Stripe carefully, explain what it finds, export useful account details, and prepare reviewed change plans before anything touches live billing or money-moving flows.

Use it for questions like: "Which subscriptions are active?", "Why did this customer get charged?", "What refunds or disputes need review?", "Which connected account is this payout for?", or "Can you draft a safe metadata cleanup plan first?"

Live Stripe work is intentionally cautious. Reads need `--live`, writes start as review plans, money-moving actions need stronger approval, and when there is no saved snapshot or provider backup the tool requires explicit no-snapshot approval before Stripe HTTP.

A good first ask is: "Check the Stripe skill is connected, show me the account details, list recent customers and subscriptions, and stop before any writes."

## Start here first

- Want ideas for real Stripe work? [What you can do with Stripe](docs/use_cases.md)
- Need setup? [Connect your Stripe account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review Stripe account details, customers, subscriptions, invoices, products, prices, payouts, refunds, and disputes.
- Export Stripe reads for finance review, support work, reconciliation, or cleanup planning.
- Build careful metadata, catalog, billing, or account-change plans before anything touches live Stripe data.
- Check connected-account targets when a job needs `--stripe-account`.
- Reach the broader documented Stripe API surface when you need a real Stripe operation that does not already have a smaller front door.

## What access this skill needs

- A Stripe API key.
- The right Stripe mode for the work you want to do, usually test first and live later.
- If you work on a connected account, the target `acct_...` account ID.
- If your team uses a connected-account allowlist, the target account must already be approved there.

## Install and first run

Install slug: `stripe`

Ask your agent to install the `stripe` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@stripe -g -y
```

Then try a safe first ask like:

```text
Check the Stripe skill is connected, show me the account details, list recent customers and subscriptions, and stop before any writes.
```

## How this skill stays safe

- Read work does not hit Stripe unless you add `--live`.
- Write-like operations start as plan-only output first.
- Write retries keep a stable idempotency key so the same Stripe action is not sent twice by accident.
- Higher-risk operations like payments, payouts, transfers, refunds, and deletes need stronger approval flags such as `--yes`, `--plan-in`, `--ack-spend-money`, or `--ack-irreversible`.
- When no saved snapshot or provider backup exists, live writes still need explicit `--ack-no-snapshot`.
- Plans, receipts, run history, docs, tests, and the API coverage ledger all live in this repo.

## What it covers today

This skill covers:

- account, customer, product, price, invoice, subscription, checkout, refund, payout, dispute, and Connect review work
- explicit per-operation commands for the pinned Stripe API snapshot
- dry-run write planning with deterministic risk classification
- local run-artifact proof for plans, refusals, and receipts

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target account, operation, and recovery limit before apply.
- Live reads need `--live`.
- Normal writes need `--live --apply`.
- Higher-risk writes also need `--yes --plan-in`.
- Money-moving writes need `--ack-spend-money`.
- Irreversible deletes also need `--ack-irreversible`.
- When no saved snapshot or provider backup exists, live write apply also needs `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Reviewed plans can be replay-checked with `--plan-in`.
- Local run history lives under `.state/runs/`.
- The docs, tests, proof pack, and API coverage ledger are all in this repo.

## Limits

- This tool does not promise automatic rollback or snapshot-based restore.
- Live Stripe work still depends on valid account access and the correct test or live key.
- When no saved snapshot or provider backup exists, recovery is manual follow-up work, not one-click undo.
- Some connected-account work can be refused if the target account is outside the allowlist.

## Helpful docs

- [Browse all Stripe docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
