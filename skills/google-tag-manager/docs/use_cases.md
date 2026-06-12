# Use cases

Use this page when you want ideas for real Google Tag Manager jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "List my GTM accounts, containers, and workspaces."
- "Review the tags, triggers, and variables in this container before we publish anything."
- "Compare these GTM versions and explain what changed."
- "Show me which workspace changes are waiting for review."
- "Prepare a dry-run plan for this tag or variable change and stop before apply."

## What to expect back

The agent should give you a clear map of the GTM account, container, workspace, and resource it checked. For review work, it should summarize the tags, triggers, variables, versions, or publish state in plain English.

For changes, the agent should slow down. It should show a dry-run plan first, ask for approval before apply, and explain when a GTM method cannot safely run live because the API does not expose the needed pre-read.

## Good fits

- tracking setup reviews
- tag, trigger, and variable inventories
- version comparisons
- publish-readiness checks
- careful API change plans

## Not a good fit

- deciding marketing strategy from tag names alone
- publishing a container without a reviewed plan
- assuming a tag fires correctly without website-side testing
- broad undo promises for GTM changes
