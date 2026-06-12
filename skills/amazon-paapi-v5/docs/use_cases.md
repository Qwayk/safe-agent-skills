# What you can do with Amazon Product Advertising API

Amazon Product Advertising work usually starts with a simple question: "Which products are real candidates, and can I trust the data before I write about them?"
If you need setup first, start with [Connect your Amazon Associates credentials](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill is best for structured product research and affiliate-link work. It gives your agent real Amazon catalog data instead of page scraping guesses.

## Common jobs this skill is good at

- Find candidate products for a niche, gift guide, comparison page, or shortlist.
- Fetch exact product details for a known set of ASINs.
- Clean up raw Amazon product URLs and resolve them into ASINs first.
- Build affiliate links from the ASINs you already trust.
- Check browse nodes or category IDs before a larger research pass.
- Run a CSV batch file for repeatable research work.

## Real example asks

- "Search Amazon for cast iron skillets and give me 10 products worth reviewing."
- "Fetch product details for these ASINs and give me a clean structured summary."
- "Resolve these Amazon links into ASINs and build affiliate links for each one."
- "Run this CSV batch file and tell me which rows worked and which rows failed."

## What the agent should show you

- The exact products or ASINs it checked.
- The marketplace and partner tag assumptions it used.
- A short explanation of which products look useful and why.
- Any rows that failed in a batch, instead of hiding them in the output.
- Clean affiliate links only after the product matches look right.

## What a careful run should look like

- Start with a small sample query or one ASIN first.
- Confirm the marketplace and credentials are correct.
- Expand to a bigger pull only after the first result looks right.
- Save the output when you want a review trail or reusable dataset.
