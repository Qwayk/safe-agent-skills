# What you can do with Google Ads

Google Ads work usually starts with a spend question: which accounts are accessible, where money is helping, where it is leaking, which search terms or placements need review, and which campaign change is safe enough to plan next.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Media buyer quickstart](media_buyer_quickstart.md), [Quickstart](quickstart.md), and [Command reference](command_reference.md).

This skill helps an agent export campaign evidence, explain performance patterns, and prepare budget, negative keyword, conversion upload, or campaign-build plans before anything changes a real ad account.

## Good jobs to give the agent

### Account and performance review

- "Show which Google Ads accounts I can access and confirm the customer IDs."
- "Export the optimization pack for the last 30 days and summarize the biggest issues before we change anything."
- "Compare two date ranges and explain what changed without claiming causality from the report alone."
- "Show campaign, ad group, keyword, search term, placement, landing page, device, network, and conversion-action patterns."
- "Build a shortlist of campaigns or keywords that deserve human review and explain why each one was picked."

### Search terms, placements, and budget checks

- "Find search terms that look wasteful, irrelevant, or worth adding as keywords."
- "Review placements, landing pages, devices, and time-of-day data before we change targeting."
- "Check budgets, bid strategy, Maximize Clicks ceilings, and spend pacing before we adjust anything."
- "Show the evidence behind a negative keyword, budget, or campaign pause recommendation."

### Reporting and field discovery

- "Run a small GAQL read to answer this custom question and export the result to JSON."
- "Help me discover which Google Ads fields exist for this report so I do not guess the schema."
- "Export a deeper analysis pack for placements, landing pages, schedules, networks, and conversion breakdowns."
- "Tell me which tables support this diagnosis before running a broad account pull."

### Careful change planning

- "Preview a budget change and explain the spend risk before live apply."
- "Prepare a negative keyword plan from this reviewed list."
- "Prepare a conversion upload plan and show exactly what would be sent."
- "Build a strict Search campaign plan from this reviewed spec file."
- "Explain allowlist, spend, irreversible, or no-snapshot approvals before any live write."

## What the agent should show you

- The customer ID, manager login, date range, report pack, GAQL query, campaign, keyword, placement, or entity it used.
- The evidence behind each recommendation, with a clear note when the result is descriptive and not proof of cause.
- A dry-run plan before budgets, negative keywords, uploads, removes, campaign builds, or other account changes.
- Any local write allowlist, global kill switch, spend, remove, irreversible, or no-snapshot gate that affects the request.
- A receipt, refusal, read-back check, or saved export path after the request.

## Good first Google Ads path

Start by checking account access, choosing the right customer ID, exporting `optimization_pack_v1` for the last 30 days, and asking the agent to summarize the biggest issues before planning any change.
