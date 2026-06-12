# What you can do with Meta Ads

Meta Ads work usually starts with performance questions: what changed, which campaign or creative deserves attention, and what data should be exported before a human decides what to change.
If you need setup first, start with [Connect your Meta Ads account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Inventory and account checks

- “List my ad accounts with id + name.”
- “List campaigns in act_<id> with id, name, status.”
- “List ads in act_<id> with id, name, status, effective_status.”
- “List creatives in act_<id> and fetch a specific creative by id.”

## Insights and reporting

- “Campaign performance last 7 days: impressions, clicks, spend.”
- “Daily spend for January 2026 with breakdowns.”
- “Adset-level insights for a specific time range.”
- “Compare two date ranges (same settings) to spot fatigue or promotion effects.”

## Analysis packs and creative review

- “Export an analysis-ready snapshot pack (manifest + JSONL tables).”
- “Find winning ads and inspect their creative anatomy + previews.”
- “Optionally download creative asset URLs into the export (explicit opt-in).”

## What the agent should show you

Because this tool is read-only, the agent should:

1. check auth first
2. name the ad account, date range, and level it used
3. summarize what changed or what looks worth reviewing
4. point to any local export files it created
