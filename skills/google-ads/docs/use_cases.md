# Use cases

Use this page when you want ideas for real Google Ads jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Common use cases (examples)

- “Show me which Google Ads accounts I can access, and their customer ids.”
- “Export a joinable analysis pack for last month so I (and an AI agent) can find winning ads and explain why they win.”
- “Export a maximal pack (placements, landing pages, time-of-day, network, conversion-action breakdowns) for deeper diagnosis.”
- “Compare two packs (two date ranges) and summarize the descriptive differences (no causal claims).”
- “Run a GAQL query to pull a small sample of campaign performance fields (for exploration) and export to JSON.”
- “Help me discover which fields exist for a report (so I don’t guess the schema).”
- “Build a shortlist of underperforming campaigns based on a pack export and explain why they were picked.”

## What this tool intentionally does not do

- It does not “optimize” or claim causality; exports are descriptive only.
- It does not perform external writes without explicit approval and a configured allowlist (safe-by-default refusal is the intended behavior).

For edits:
- Use the explicit RPC method commands, run once to get a plan, review it, then apply with the required safety gates (see `docs/safety_model.md`).
