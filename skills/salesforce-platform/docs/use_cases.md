# Use cases

Use this page when you want practical Salesforce Platform jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

Salesforce Platform work is usually about understanding the org before changing it. The agent can help you look at records, metadata, limits, jobs, and API resources first, then prepare a plan if something needs to change.

## Good jobs to give the agent

- "Show the org REST resources and limits before we plan anything."
- "Run this Account query and explain the result in simple English."
- "Show the fields and metadata for this object."
- "Check list views, quick actions, layouts, or approval metadata for this object."
- "Review this Bulk API job and tell me whether it finished or failed."
- "Prepare a composite request plan and wait for my approval before applying it."
- "Check org-gated areas like Knowledge, consent, scheduler, or survey translations if this org exposes them."

## What the agent should show you

When a change is requested, the agent should:

1. Show the dry-run plan first.
2. Name the org, object, query, or job it is working with.
3. Explain any missing permission or org feature clearly.
4. Ask for stronger approval before high-risk or irreversible changes.
5. Say plainly when a live apply has no saved before-state and needs no-snapshot approval.
