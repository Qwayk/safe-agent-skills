# Use cases

This tool helps publishers, affiliate teams, and ad or revenue teams who need direct answers from Sovrn without clicking around dashboards all day.

It is best for people who want an AI agent to do safe read-only work like:

- checking whether a product URL can be monetized
- pulling Commerce reports by page, link, merchant, network, merchandise, or CUID
- finding approved merchants for a campaign
- comparing prices for one product across merchants in one market
- pulling Advertising account, bid, breakout, domain, or custom reports

## Why this beats typical no-code automation

Typical no-code automation is good when you already know the exact record or trigger and just want “when X happens, do Y.”

This tool is better when the hard part is discovery, targeting, and report pulling:

- it can ask the real Sovrn APIs direct questions
- it can search across existing campaigns, merchants, products, and reports
- it gives deterministic API results instead of browser scraping
- it handles the real Sovrn auth split without making you guess which key type belongs to which job

## Discovery example

Imagine you are planning a shopping guide and you do not know the best merchants or product offers yet.

An AI agent can:

- pull the approved merchants for your campaign
- check whether the product URLs you found can be monetized
- compare alternative merchants and prices for the same product
- pull recent Commerce report data so you can see which pages or merchants already perform well

That kind of discovery work is where this tool is much stronger than a simple no-code workflow.

## Who it helps most

- Commerce publishers who need cleaner research before placing affiliate links
- revenue teams who want fast exports from Sovrn reporting endpoints
- ad or ops teams who need Advertising report pulls without manual dashboard work
- AI-agent workflows that need safe, explicit, read-only commands instead of a generic raw API bridge

## Honest limits

- This shipped surface is read-only.
- It does not claim browser-only JavaScript docs as shipped CLI coverage.
- It does not claim MCP beta pages as shipped CLI coverage.
- It does not flatten Commerce and Advertising auth into one fake key.
