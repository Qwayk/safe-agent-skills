# Use cases

Use this page when you want ideas for real PayPal jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## What this tool is good for

- Check whether your PayPal app is connected and ready
- Look up an order, capture, refund, webhook, invoice, product, plan, or subscription by ID
- Prepare a safe preview before creating or updating PayPal data
- Keep a local history of write previews and refusals

## Common requests you can give an agent

- “Check the PayPal connection and tell me what is ready.”
- “Show me this order and explain its status in simple English.”
- “List my webhooks and tell me which events each one listens to.”
- “Prepare a preview for creating a draft invoice. Do not apply it yet.”
- “Look up this captured payment and tell me whether it was refunded.”
- “List my subscription plans and show the details for plan P-123.”
- “Prepare a safe delete command for this payment token, but stop before the final step.”

## Areas with extra limits

Some PayPal products are only available when your account or partner setup allows them.
Examples include partner referrals, payouts, referenced payouts, some dispute actions, and some reporting paths.

The tool still ships those documented commands, but it marks them clearly in `docs/api_coverage.md` and `docs/proof.md`.

## What safe behavior looks like

For reads, the agent can run the command directly.

For writes, the agent should:

1. show the dry-run plan first
2. wait for approval before `--apply`
3. add `--yes` for any risky action when the command requires it, not only deletes
4. show the safe refusal result when required approval is missing, or the receipt when an approved supported write proceeds
