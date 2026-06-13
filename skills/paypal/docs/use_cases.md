# What you can do with PayPal

PayPal work usually starts with a money or customer question: did this order complete, was a capture refunded, which invoice or subscription is active, and what webhook or payout needs review?
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent read PayPal records, explain their status, and prepare preview-first changes without treating payments, invoices, disputes, payouts, or subscriptions like harmless data.

## Good jobs to give the agent

### Orders, payments, refunds, and tracking

- "Show me this order and explain its status in simple English."
- "Look up this captured payment and tell me whether it was refunded."
- "Check an authorization, capture, refund, or payment token before support replies to the customer."
- "Find eligible payment methods for this context and explain what PayPal returned."
- "Review tracking information for this order before we update anything."

### Invoices, products, plans, and subscriptions

- "List my subscription plans and show the details for plan P-123."
- "Show this subscription and explain whether it is active, suspended, canceled, or past due."
- "Prepare a preview for creating a draft invoice, but do not apply it yet."
- "Review invoice search results for this customer before we send a reminder."
- "Check products and plans before we change pricing or subscription setup."

### Webhooks, disputes, payouts, and partner areas

- "List my webhooks and tell me which events each one listens to."
- "Verify this webhook signature request and explain the result."
- "Review this dispute and show which actions may be available."
- "Check payout or referenced-payout access and tell me if the account is gated."
- "Review partner-referral or reporting commands, but tell me when the PayPal account may not have access."

### Preview-first changes

- "Prepare a safe preview before creating or updating PayPal data."
- "Prepare a safe delete command for this payment token, but stop before the final step."
- "Show the required approval flags before any risky PayPal apply."

## What the agent should show you

- The PayPal mode, object ID, command family, and action it checked.
- The plain-English status of the order, capture, refund, invoice, product, plan, subscription, webhook, dispute, payout, or token.
- Any account, partner, payout, dispute, or reporting gate that may block the request.
- A dry-run plan before any create, update, delete, cancel, capture, refund, payout, or dispute action.
- A safe refusal when required approval is missing, or a receipt when an approved supported write proceeds.

## Good first PayPal path

Start with `auth check`, read one known order or webhook, then ask the agent to explain which PayPal families your account appears ready to use before planning any write.
