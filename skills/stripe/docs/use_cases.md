# What you can do with Stripe

Stripe work usually starts when billing, money movement, or customer support needs a careful answer: why was someone charged, which subscription is active, what invoice is unpaid, which refund or dispute needs review, and which connected account owns the money?
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent inspect Stripe records, export useful review data, and prepare change plans before anything touches live billing, payments, payouts, transfers, or customer records.

## Good jobs to give the agent

### Customer and billing review

- "List recent customers with email, creation date, and account status."
- "Show subscriptions that are trialing, active, past due, paused, or canceled."
- "Find invoices that are open, overdue, uncollectible, or recently paid."
- "Explain why this customer was charged by checking the customer, invoice, subscription, payment intent, and charge."
- "Export recent customers, subscriptions, invoices, and failed payments for finance review."

### Catalog, pricing, and cleanup planning

- "List products and prices so I can see what is currently sold."
- "Find products or prices missing metadata and prepare a cleanup plan."
- "Draft a metadata update plan for these product, price, customer, or subscription IDs and stop before any writes."
- "Review checkout sessions, payment links, coupons, or promotion codes before we change a campaign."

### Refunds, disputes, payouts, and transfers

- "Prepare a refund plan for this payment and explain every approval gate before live apply."
- "Review recent refunds and disputes and tell me what needs human attention."
- "Review payouts and transfers and flag anything unusual."
- "Check which connected account this payout, charge, customer, or transfer belongs to."
- "Show whether this job needs money-moving approval before any live Stripe call."

### Connect and account operations

- "Check this connected account safely and show me what data is available before we plan any changes."
- "List account details and capabilities for this connected account."
- "Check whether this connected account is allowed by the local allowlist."
- "Prepare a careful account, capability, or external-account change plan, but stop before apply."

## What the agent should show you

- Whether it is using test mode or live mode.
- The customer, subscription, invoice, payment, refund, dispute, payout, transfer, product, price, or connected account it checked.
- A short plain-English explanation before any raw Stripe data.
- A dry-run plan before any write-like operation.
- Stronger approval gates for money-moving, irreversible, connected-account, or no-snapshot work.
- The saved plan, receipt, refusal, or run history after the request.

## Good first Stripe path

Start with an account check, list recent customers and subscriptions, then inspect one real customer or invoice end to end before planning any update.
