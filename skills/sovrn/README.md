# Sovrn

See which pages, links, and merchants earn money through Sovrn Commerce, or pull an Advertising report for a publisher. You can also check whether a product link can earn for one of your sites before you add it to a page.

Start with “Which pages earned the most last week?” or “Can this link earn on my site?” Your agent checks which Sovrn key you have, runs the matching report or link check, and tells you what the result means.

The tool reads account data and requests estimates or recommendations. You decide what to do with the results, including where to use a link or share a report.

## Start here first

- [Run your first report or link check](docs/quickstart.md)
- [Find the right key for your job](docs/onboarding.md)
- [See what you can ask your agent](docs/use_cases.md)

## What your agent can do

- List Commerce campaigns and approved merchants.
- Check links, compare prices, and find coupons or product suggestions where your account has access.
- Read Commerce earnings by page, link, merchant, product, or transaction.
- Read Advertising results for a publisher, domain, or ad placement.

## What access this tool needs

A Commerce site API key checks links. A Commerce secret key reads earnings and approved merchants. Coupons and price comparisons use both Commerce keys. Advertising reports use an Advertising key and publisher ID. [Setup and connection help](docs/onboarding.md)

## Install and first run

Ask your agent to install the `sovrn` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@sovrn -g -y
```

The skill includes the guides and source for the `sovrn-safe-cli` command. [Install and run the command](docs/quickstart.md)

## Limits

A link check applies to the key's site and any country you selected. It tells you whether the URL can earn, and earnings and approval status need their own checks. The merchant list returns one page per request. [Understand the results](docs/safety_model.md)

## Helpful docs

[All Sovrn guides](docs/README.md)
