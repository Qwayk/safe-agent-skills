# Use cases

Use this page when you want ideas for real LinkedIn Ads jobs to hand to your agent.
If you need setup first, start with [Connect your LinkedIn Ads account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with LinkedIn Ads work

LinkedIn Ads work often breaks in two places: getting the right product approval, and making sure the account or campaign change is really the one you meant. This tool helps by:

- showing which product, tier, or private-API gate is in the way
- giving you dry-run plans before live LinkedIn changes
- keeping one explicit command path per documented family instead of asking the model to guess from scattered docs
- leaving local proof files behind so you can review what was planned and what really ran

## Common use cases (examples)

- “Check my LinkedIn Ads token, tell me which ad accounts I can access, and flag any approval problems.”
- “Show campaign groups, campaigns, and one analytics pull for this ad account.”
- “Review my creatives and previews before I change anything.”
- “Prepare a campaign update plan and stop before any live apply.”
- “Show which lead forms, lead responses, or conversions are available in this account.”
- “Check whether tracking tags, insight tags, or audience-related families are accessible with this app.”

## Approval-gated areas to expect

LinkedIn often blocks or limits these areas until app approval is complete:

- Matched Audiences
- Audience Insights
- Media Planning
- Company Intelligence
- some Lead Sync, Conversions, tracking, and creative flows depending on account tier and product access

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Check whether the token, product approval, and account access are in place.
2) Show the dry-run plan before any live LinkedIn write.
3) Explain any extra gates like `--yes`, `--plan-in`, or no-snapshot approval.
4) Point to the saved plan and run artifacts after the review step.
