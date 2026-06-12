# What you can do with Figma

Use this page when you want practical Figma jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

Figma work is usually about understanding a file, library, comment thread, or team resource before making a design-system or workflow change.

## File and comment review

"Show me the latest file metadata, version history, and unresolved comments for this file."

An agent can inspect file JSON, metadata, versions, comments, and reactions before anyone changes anything.
This is a good first step when you need to understand a file quickly without clicking through the UI.

## Design system and library audit

"List the components, styles, variables, and library analytics for this team or file."

This helps when you want a clean view of your design system, published library state, or variable usage before a migration or cleanup pass.

## Safe change planning

"Draft a comment, webhook, variable, or dev-resource change, show me the exact plan, and wait for approval."

The skill can preview supported writes first, show the target and request body, and stop before anything goes live.
If Figma does not expose useful before-state, the reviewed apply still needs explicit no-snapshot approval.

## Access and plan check

"Tell me which endpoints this token can use now, and which ones depend on team, org, or plan access."

This is useful before you promise automation work or start a deeper rollout.
It helps separate what is already available from what is gated by workspace tier or permissions.

## Proof and handoff

"Save the plan, receipt, or JSON output so I can review it later or hand it to someone else."

The skill keeps local run history, saved plans, receipts, and reusable JSON outputs.
That makes it easier to audit what was reviewed, previewed, or applied.

## What the agent should show you

When you ask for a change, the agent should:

1. Name the file, team, project, variable, dev resource, comment, or webhook target.
2. Show the relevant read result before planning the change.
3. Show the dry-run plan before any live Figma write.
4. Explain team, organization, plan, or no-snapshot limits clearly.
5. Point to saved plans, receipts, or JSON output when you need proof or handoff material.
