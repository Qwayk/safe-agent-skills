# What you can do with Sovrn

Sovrn is useful when a publisher needs to understand affiliate revenue, merchant options, link monetization, or advertising reports without clicking through dashboards by hand.

This skill helps an agent pull Sovrn Commerce and Advertising data in a structured way. It is strongest for research and reporting: checking whether URLs can earn, finding approved merchants, comparing product offers, and exporting the reports a publisher needs before making content or revenue decisions.

If you need setup first, start with [Connect your Sovrn account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "Check whether the Sovrn credentials are ready, then show which Commerce and Advertising areas can be used."
- "Find approved merchants for this campaign and explain which ones look useful."
- "Check whether these product URLs can be monetized."
- "Pull recent Commerce performance by page, link, merchant, or transaction."
- "Pull an Advertising report for this account and summarize the main changes."

## Publisher jobs this helps with

Sovrn is most useful when the agent can turn raw revenue data into a decision:

- "Which buying-guide pages earned last week, and which merchants drove that revenue?"
- "Which product links should we keep, replace, or investigate?"
- "Which merchants are approved for this campaign before we write the article?"
- "Which domains or ad placements changed in the latest Advertising report?"
- "Which transactions, CUIDs, or merchandise rows need a closer look?"
- "Can you export this report so I can hand it to the editor or revenue team?"

These are normal publisher questions. The value is not just pulling JSON; it is helping someone see what to do next.

## Shopping-guide research

For a product article, a good agent flow looks like this:

1. Check the campaign and merchant context.
2. Look up whether the product URLs can be monetized.
3. Compare available merchants and prices for the same product.
4. Pull recent Commerce reporting for similar pages or links.
5. Return a short recommendation: which merchants look usable, which links need caution, and what still needs human review.

That turns Sovrn into a research helper before a writer or editor commits to a product set.

## Reporting and handoff

Good report asks include:

- "Give me a clean page-level revenue summary for this date range."
- "Compare merchant performance between these two periods."
- "Find transactions tied to this CUID and explain what they show."
- "Pull Advertising account, bid, breakout, domain, or custom reports and save the output."

The agent should name the report type, date range, account or campaign, and any filters it used. If a report is empty, it should say whether the most likely cause is credentials, filters, date range, or no matching data.

## What good output looks like

A useful Sovrn answer should include:

- the account or credential check result
- the report or Commerce area used
- the date range and filters
- the most important rows or patterns
- a short explanation for a publisher, not just raw data
- a saved file path when the output is too large for chat

## Honest limits

This shipped tool is read-only. It does not manage browser-only JavaScript setup, and it does not pretend the Commerce and Advertising APIs use one simple key. If credentials or publisher IDs are missing, the agent should stop and explain the missing piece.
