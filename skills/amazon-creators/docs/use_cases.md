# Use cases

Use this page when you want practical Amazon Creators jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with Amazon catalog research

Amazon Creators work often means comparing books, formats, browse nodes, variations, and locale-specific catalog data before a content or catalog decision is made.

The agent is most useful when it turns ISBNs, ASINs, resource presets, and locales into a clear request plan before calling Amazon.

## Good jobs to give the agent

- “Gather every classification, variation summary, and parent ASIN for this set of ISBNs so I can compare paperback, hardcover, and Kindle formats.”
- “Document the browse-node hierarchy for a niche category so we know the canonical navigation path before we redesign the catalog copy.”
- “Confirm the locale mapping before we place an order so the marketplace header matches the region we care about.”
- “Collect simplified technical info for multiple formats and send me both the plan (dry-run) and the receipt once the live data arrives.”
- “Search for these book keywords and compare the best matches by format and locale.”
- “Show me which resource presets this tool supports before we choose the final request shape.”

## What the agent should show you

When you ask for a catalog request, the agent should:

1. Show a dry-run plan that lists the locale, resources, identifiers, and parameters.
2. Wait for confirmation before calling Amazon.
3. Return a simplified data view, request summary, and receipt after approved catalog apply.
4. Keep tokens, secrets, and raw headers out of logs.
5. Say clearly when a credential, locale, or identifier does not match the request.
