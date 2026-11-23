# Skimlinks

Find merchants for the market you cover, see which pages and links earned commission, and look up alternatives for products you write about. You can also make a Skimlinks URL for a newsletter, social post, or anywhere you need to place an affiliate link yourself.

Try asking, "Which merchants sell running shoes in the US?" or "Which links earned the most commission last month?" Your agent checks that it has the right account, then runs the search or report and explains what came back.

The tool reads from Skimlinks and builds links on your computer. When it makes a link, it gives you the URL to review and use.

## Start here first

- [Connect your Skimlinks account](docs/onboarding.md)
- [Run your first command](docs/quickstart.md)
- [See what you can ask](docs/use_cases.md)

## What your agent can do

- Find merchants, their domains, available offers, and merchant categories.
- Check commissions, page and link performance, payment status, and merchants that were removed.
- Look up one product or a list of products and see the alternatives Skimlinks returns.
- Build an affiliate link with an optional tracking label and referring page.

## What access this tool needs

Merchant and reporting commands use your publisher ID and the Client ID and Client Secret from Publisher Hub. Product Key also needs a publisher domain ID. Skimlinks may give you a separate set of credentials for it. Link Wrapper uses the Site ID for the site where you’ll place the link.

## Install and first run

Ask your agent to install the `skimlinks` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@skimlinks -g -y
```

Open [Quickstart](docs/quickstart.md) to set up the Python command and run your first read.

## Limits

A Product Key sign-in check confirms that the credentials can get a token. A lookup tells you whether they can read product data. Affiliate links can earn commission when the merchant and your site are eligible. Data Pipe exports and Skimlinks JavaScript have their own setup in Publisher Hub and developer docs.

## Helpful docs

- [Guide index](docs/README.md)
- [Command guide](docs/command_reference.md)
- [How the tool handles your account and data](docs/safety_model.md)
- [What we checked](docs/proof.md)
- [API coverage](docs/api_coverage.md)
