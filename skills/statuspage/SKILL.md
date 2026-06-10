---
name: statuspage
description: Check a public status page and summarize status, incidents, maintenance, and affected components.
---

This page is the agent-facing rule sheet for the public Statuspage skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


# Statuspage

Use this skill when the user wants a quick answer from a public status page.

## When to use this

- the user wants to know if a service is down
- the user wants open incidents from a public status page
- the user wants planned maintenance from a public status page
- the user wants a simple summary of current component status

## What this skill does today

This skill checks public status pages served by Statuspage only.

It can report:

- the overall status
- open incidents
- planned maintenance
- listed components when the page provides them

Do not act like this skill can log into a private account, create incidents, update incidents, or change components.

If the user asks for private-account or write actions, say that this skill only checks public pages right now.

## Setup

- If the user already gave a public Statuspage URL, use it.
- If the URL is missing, ask for the public status page URL.
- Do not ask for an API key for the normal public-page flow.
- If the host agent needs a restart to load new skills, remind the user to restart it first.

## How to work with this safely

- Stay read-only.
- Do not claim private access.
- Do not invent incidents or components.
- If information is missing, say it is missing.
- Include the source page URL in the result so the user can check it too.

## Result shape

- Keep the summary short and clear.
- Start with the overall status.
- Then list open incidents and planned maintenance if they exist.
- Mention affected components when the page shows them.
- Include the source page URL in the result.

## Limits

- public Statuspage pages only
- no private-account access
- no writes

## Helpful docs

- `docs/safety_model.md`
- `docs/command_reference.md`
- `docs/api_coverage.md`
- `examples/first-run.md`
