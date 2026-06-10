# Use cases

Use this page when you want ideas for real Salesforce Platform jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This tool is good when you want an agent to work against standard Salesforce Platform REST resources without guessing.

Common examples:

- inspect org REST resources, limits, tabs, themes, or object metadata
- run SOQL or SOSL safely, including paged query follow-ups
- read sObject records and prepare write review plans without sending unsafe provider writes
- upload or download blob fields through documented sObject flows
- inspect list views, quick actions, layouts, approval metadata, and Lightning usage metrics
- work with composite requests and Bulk API 2.0 jobs
- read org-gated areas like Knowledge, consent, scheduler, survey translations, and Named Query APIs when the org exposes them

What makes this safer than ad hoc API calls:

- writes are dry-run first
- current write apply requires explicit no-snapshot approval before Salesforce HTTP until before-state capture exists
- destructive actions need extra confirmation
- run history is saved locally
- the command surface is tied to official Salesforce docs and explicit scope boundaries
