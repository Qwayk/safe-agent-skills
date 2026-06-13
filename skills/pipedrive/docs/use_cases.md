# What you can do with Pipedrive

Pipedrive work usually starts with a sales question: which deals need attention, which people or companies are already in the CRM, what activities are overdue, and what should a salesperson review next?
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill is read-only. That makes it best for sales review, cleanup planning, handoff prep, and CRM research before someone uses another approved workflow to change records.

## Good jobs to give the agent

### Deal and pipeline review

- "Show open deals in this pipeline and group them by stage."
- "Find deals with no recent activity and flag the ones that may need follow-up."
- "List won and lost deals from last month so I can review what changed."
- "Check this deal and show the linked person, organization, notes, products, files, and activities."
- "Compare pipeline stages and tell me where deals are getting stuck."

### Contact and company research

- "Check whether this person or organization already exists before we create a duplicate."
- "Find people connected to this organization and show their open activities."
- "Search for this email, phone number, or company name and summarize the matching CRM records."
- "Pull notes and activity history for this contact before a sales call."

### Follow-up and handoff work

- "Show overdue activities for this owner so we can prepare a follow-up list."
- "Find upcoming calls, meetings, or tasks for this week."
- "Create a sales handoff summary for this account using deals, people, organizations, notes, and activities."
- "Pull product, file metadata, and timeline details for this customer so another agent can draft a next-step plan."

### Account setup and reporting checks

- "List users, roles, pipelines, stages, fields, filters, goals, and permissions so I understand this Pipedrive account."
- "Show which custom fields exist on deals, people, organizations, products, and activities."
- "Check goals or permissions before I ask a human to change the CRM setup."

## What the agent should show you

- The Pipedrive domain and token check result, without exposing the token.
- The exact record type it reviewed: deal, lead, person, organization, activity, product, note, file metadata, pipeline, stage, field, filter, goal, user, role, or permission.
- A short plain-English summary before any raw JSON.
- The IDs and links a human would need for follow-up.
- A clear stop if the job requires creating, updating, deleting, or downloading file content, because this skill only reads.

## Good first review path

Start with auth, list a few deals, people, and activities, then ask the agent to summarize what looks worth reviewing. After that, narrow the request to one pipeline, owner, contact, company, or deal.
