# What you can do with Klaviyo

Klaviyo work usually starts with audience and message questions: which people are in the right group, which campaigns or flows need attention, and which bulk actions need a plan before they touch customers.
If you need setup first, start with [Connect your Klaviyo account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

- "Show me which lists, segments, forms, or campaigns match these filters."
- "Check one profile, event stream, or metric before I change anything."
- "Prepare a safe bulk import, subscribe, suppress, or unsubscribe change, then show the plan for review."
- "Plan catalog, coupon, template, webhook, or form changes from reviewed JSON."
- "Plan a send cancellation or delete action and show me the recovery limit before apply."
- "Use the client endpoints for signup, reviews, push tokens, or event capture when I only have the company id."

## What you should expect from the agent

For review work, the agent should show the account object, filters, date range, or operation it used before it summarizes the result.

When you ask for a change, the agent should:

1. Show a dry-run preview of what would change.
2. Explain the recovery limit before any live write runs.
3. Require explicit no-snapshot approval when no saved snapshot is available.
4. Refuse apply safely if someone skips the required approval gates.
5. Point to the saved plan, receipt or refusal summary, and proof files.
