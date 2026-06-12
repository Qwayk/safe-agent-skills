# PayPal

**Capability:** Reads + careful changes

PayPal is where orders, captures, refunds, invoices, subscriptions, payouts, webhooks, and app setup can quickly turn into customer support or finance work.

This skill helps an agent check what PayPal knows, explain statuses in plain English, and prepare write previews before anything is sent to PayPal as a live change.

Use it for questions like: "Is my PayPal app connected?", "What happened with this order?", "Was this captured payment refunded?", "Which webhook events are active?", or "Can you draft the invoice first and stop before sending it?"

Reads still need real PayPal credentials and the right account access. Writes are preview-first, and current write apply requires explicit no-snapshot approval before PayPal auth or HTTP until command-specific saved snapshot support is available.

A good first ask is: "Check the PayPal connection, tell me which API areas are ready, show one safe read example, and stop before any writes."

## Start here first

- Want ideas for real PayPal work? [What you can do with PayPal](docs/use_cases.md)
- Need setup? [Connect your PayPal account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check PayPal app readiness and credential setup.
- Look up orders, captures, refunds, invoices, webhooks, products, subscriptions, and payment tokens by ID.
- Review webhook event types and PayPal object statuses before planning changes.
- Prepare safe previews for invoices, tokens, tracking, subscription, payout, and partner-related work where your account allows it.
- Keep local proof for plans, refusals, and supported receipts.

## What access this skill needs

- A PayPal REST app client ID and client secret.
- Sandbox credentials first, usually with `PAYPAL_ENVIRONMENT=sandbox`.
- Production-approved credentials before live account work.
- The right PayPal account or partner access for gated areas such as payouts, partner referrals, some disputes, and reporting paths.

## Install and first run

Install slug: `paypal`

Ask your agent to install the `paypal` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@paypal -g -y
```

Then try a safe first ask like:

```text
Check the PayPal connection, tell me which API areas are ready, show one safe read example, and stop before any writes.
```

## How this skill stays safe

- Read commands need valid credentials and account access.
- Write commands start as dry-run plans.
- Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP until command-specific saved snapshot support is available.
- Some higher-risk actions require `--yes`; the API coverage file names those exact commands.
- No shipped PayPal command in this tool currently requires `--ack-irreversible`.
- The tool does not create snapshots, provider backups, or automatic rollback.

## What it covers today

This skill covers:

- orders, order tracking, payments, authorizations, captures, refunds, and vault tokens
- products, plans, subscriptions, invoices, and webhooks
- payouts, referenced payouts, partner, dispute, and reporting paths where PayPal documents them publicly
- local proof for plans, refusals, run history, and API coverage

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the PayPal object, action, account context, and recovery limit.
- Riskier writes need `--yes` when the command requires it.
- Current apply still requires explicit no-snapshot approval before PayPal auth or HTTP.
- Gated PayPal areas may still refuse or fail if your account does not have access.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Reviewed plans can be replay-checked with `--plan-in`.
- Supported apply receipts can be saved with `--receipt-out`.
- Local run history lives under `.state/runs/`.
- The docs, tests, proof pack, and API coverage ledger are all in this repo.

## Limits

- Some PayPal areas are account-gated, partner-gated, or live-unverified in this build environment.
- Live reads and writes depend on valid PayPal credentials, account permissions, and sandbox or production mode.
- The tool does not promise automatic rollback or snapshot-based restore.
- Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP when command-specific saved snapshots are not available.

## Helpful docs

- [Browse all PayPal docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Examples](docs/examples/)
