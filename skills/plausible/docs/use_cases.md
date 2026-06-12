# Use cases

Use this page when you want practical Plausible jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

Plausible work is usually about answering a simple business question from clean analytics data, then stopping before any site or event write unless it is clearly approved.

## Good jobs to give the agent

### Reporting (read-only)

- “Generate a weekly report: top pages, sources/referrers, devices, and goal conversions.”
- “Create a ‘membership funnel’ report for the last 30 days and compare to the previous period.”
- “Run this Stats query JSON, validate it first, and export results to a file.”

### Analytics QA

- “Verify tracking is working by checking recent traffic on a specific page path.”
- “Find top entry and exit pages for the last 14 days.”

### Events (writes analytics; only with explicit approval)

- “Plan a test event to validate my conversion pipeline, but don’t send it until I approve.”
- “Send the test event with verification, and show me a receipt of what was written.”

## What the agent should show you

When you ask for anything that writes analytics data, the agent should:

1. Show the site, date range, metrics, dimensions, funnel, or event target.
2. Validate custom Stats queries before running them.
3. Show a dry-run plan before site changes or event sends.
4. Ask for extra acknowledgement when the action has no automatic restore point.
5. Verify best-effort when supported and provide a receipt.
