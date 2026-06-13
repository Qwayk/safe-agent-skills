# What you can do with HubSpot

HubSpot work usually starts when the team needs to know what is true about customers: which contacts or companies match a rule, how deals move through the pipeline, which properties exist, or whether an import, export, association, or custom object change is safe.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent inspect CRM records and settings, explain account limits, export useful data, and prepare careful plans before anything changes live HubSpot data.

## Good jobs to give the agent

### CRM record review

- "Find contacts without an owner and export their IDs."
- "Search companies in this industry and show the linked contacts."
- "List deals in this pipeline stage and explain what fields are missing."
- "Show tickets that match these rules before support follows up."
- "Read a small sample from each active object type so I know what this account exposes."

### Properties, associations, and pipeline checks

- "List the properties on deals and explain which ones are required."
- "Show all associations between these contacts, companies, deals, or tickets."
- "List association labels and limits before we create anything new."
- "Review this deal pipeline and explain what each stage means."
- "Check owners, property groups, custom object schemas, and object-library enablement."

### Imports, exports, and account readiness

- "Create an export job and tell me when the download is ready."
- "Preview this import and explain what HubSpot will accept or reject."
- "Show import errors for this job and group them by fix."
- "Tell me which token scopes, account tier, or inactive object type blocks this request."
- "Create a handoff file for a sales or support cleanup project."

### Careful CRM change planning

- "Draft a plan to add these custom properties."
- "Prepare a plan to update these contact, company, deal, or ticket records."
- "Plan an association-label or pipeline-stage change and show the risk first."
- "Define a new custom object schema, but show me the plan without applying it."
- "Explain when an archive, delete, merge, cancel, or hard-delete action needs stronger approval."

## What the agent should show you

- The object type, record ID, property, pipeline, association, schema, import, export, or owner it checked.
- A plain-English explanation of the CRM meaning before raw HubSpot data.
- Any missing scope, account-tier limit, inactive object type, or expired export download issue.
- A dry-run plan before creates, updates, archives, imports, property changes, schema changes, pipeline edits, or association writes.
- Stronger approval gates for batch, irreversible, or no-snapshot work.
- The saved plan, receipt, refusal, export status, or run history after the request.

## Good first HubSpot path

Start with `auth check`, list available CRM areas, read a small sample of contacts, companies, deals, and properties, then inspect one real record and its associations before planning any write.
