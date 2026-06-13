# What you can do with Salesforce Platform

Salesforce Platform work is usually about understanding the org before anyone changes records, metadata, jobs, approvals, or connected workflows.

This skill can inspect REST resources, limits, object metadata, records, list views, approval data, quick actions, layouts, and Bulk API jobs. It is especially helpful when a team needs a calm first read of a messy org: what exists, what is allowed, what failed, and what should be planned next.

If you need setup first, start with [Connect your Salesforce account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "Check this Salesforce connection and show the org resources and limits."
- "Describe the Account object and explain the important fields in simple English."
- "Run this SOQL query and summarize the records without changing anything."
- "Show list views, quick actions, layouts, or approval metadata for this object."
- "Check this Bulk API job and tell me whether it finished, failed, or needs attention."

## Sales and operations jobs

Good Salesforce questions usually start with a business process:

- "Which Accounts are missing the fields we need before a campaign import?"
- "Which Opportunities changed stage this week?"
- "Which Contacts match these rules, and what data quality issues should we fix first?"
- "Which approval records or layout settings might explain this workflow problem?"
- "Which API limits are close enough that we should pause a migration or batch job?"
- "Can you prepare a composite request plan, then stop before applying it?"

The agent should return a decision-ready summary, not a dump of records with no explanation.

## Metadata and org checks

Use this skill when you need to understand the shape of the org:

1. Check available REST resources and limits.
2. Describe the target object and fields.
3. Run a small query or metadata read.
4. Explain missing permissions or org-gated features.
5. Prepare a reviewed plan only after the target is clear.

This helps avoid the common mistake of planning a change against the wrong object, field, layout, or org feature.

## Bulk and integration work

For imports, exports, and integration checks, good asks include:

- "Review this Bulk API job and explain the failed rows or current state."
- "Prepare the smallest safe query for this export."
- "Check whether the org has enough API limit room for this batch."
- "Plan a composite request and show each subrequest before apply."

The agent should name the org, object, query, job, and target records clearly.

## What good output looks like

A useful Salesforce answer should include:

- the org or connection checked
- the object, query, job, or metadata area reviewed
- the useful business meaning of the result
- any permissions, limits, or org features that block the request
- the exact dry-run plan before a change
- a clear approval gate for high-risk or no-snapshot writes

## Honest limits

Salesforce behavior depends heavily on org configuration, permissions, API limits, installed features, and field-level access. If the agent cannot see an object, field, record, or feature, it should say that directly and ask for the missing access or a safer target.
