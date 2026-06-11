# What you can do with Figma

Use this page when you want real Figma jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

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

## Why this beats typical no-code automation

- It keeps the Figma REST surface explicit instead of hiding behavior behind a generic request bridge.
- It previews writes before applying them.
- It calls out no-snapshot risk honestly instead of pretending there is an undo path.
- It returns deterministic JSON and local proof files that are easier to review than screenshots or memory.
