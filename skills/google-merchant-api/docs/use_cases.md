# Use cases

Use this page when you want ideas for real Google Merchant API jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Merchant outcomes this tool is built for

This tool is best for Merchant workflows that need bulk-safe changes and proof.

- Inventory health check before changing prices, labels, stock, or taxes.
- Feed quality review to find policy or disapproved products.
- Safe campaign prep by finding product sets, countries, and promotions in one pass.
- Large updates with a dry-run first, then a current safety refusal if apply is attempted.

## Common use cases

- “Show me the top 20 disapproved products and group them by rejection reason.”
- “Find products with missing `targetCountry` data, then propose a fix plan.”
- “Build a clean list of active promotions by country before I ask for edits.”

### Discovery and targeting example

Example prompt for targeting work:
- “Help me discover products that are currently available in the US and in the `women` segment, then return 3 groups: healthy, risky, and review-needed.”

## What you’ll see from the agent

When you ask for a change, the agent should give:
1. A dry-run plan first.
2. A clear before-state note in the plan.
3. A refusal result if apply is attempted.
4. A short proof file location for the plan, refusal audit, and run summary.
