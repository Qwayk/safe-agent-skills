# What you can do with Google Tag Manager

Google Tag Manager work usually starts when tracking feels risky: a conversion tag may be missing, a trigger may be too broad, a workspace may contain unreviewed changes, or a published version may have changed what fires on the site.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent inspect the GTM account, container, workspace, tags, triggers, variables, versions, folders, templates, and environments before anyone publishes or edits tracking.

## Good jobs to give the agent

### Tracking setup review

- "List my GTM accounts, containers, and workspaces."
- "Review the tags, triggers, and variables in this container before we publish anything."
- "Find tags that look related to Google Ads, GA4, Meta, consent, or form tracking."
- "Show which triggers can fire on form submits, thank-you pages, or purchase events."
- "List variables used by this conversion tag so I can see what data it depends on."

### Version and workspace checks

- "Compare these GTM versions and explain what changed."
- "Show me which workspace changes are waiting for review."
- "Check whether this workspace has unpublished tags, triggers, variables, or templates."
- "Review environments before we decide which container version should be live."
- "Create a handoff summary for a marketer or developer before publishing."

### Careful change planning

- "Prepare a dry-run plan for this tag or variable change and stop before apply."
- "Plan a trigger cleanup, but show me exactly which resources would change."
- "Preview a container version or workspace action and explain the approval needed."
- "Tell me when a GTM method cannot safely run live because the API does not expose the needed pre-read."

## What the agent should show you

- The account, container, workspace, version, tag, trigger, variable, folder, template, or environment it checked.
- A plain-English summary of what exists and what looks risky or worth reviewing.
- The dry-run plan before any GTM write.
- A clear note when website-side testing is still needed, because the API can show configuration but cannot prove a browser event fired correctly.
- A receipt or refusal after an approved apply attempt.

## Good first tracking path

Start by listing accounts and containers, choose one workspace, review tags, triggers, and variables, then compare the latest versions before planning any change.
