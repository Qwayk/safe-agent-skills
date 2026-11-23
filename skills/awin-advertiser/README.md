# Awin Advertiser

See which publishers and campaigns drive sales for your Awin program. Your agent can pull performance reports, find specific transactions and check what happened to a batch you sent.

Start with a question like “Which publishers drove the most sales last month?” The agent checks which advertiser account it can open, then reads the report for that account and date range.

You can also ask the agent to prepare a transaction batch, create an offer, upload a product feed or send conversion orders. The agent shows you the account and what it would send, then waits for your approval. After sending, it shows what Awin confirmed and anything you still need to check.

## Start here first

- [Run your first report](docs/quickstart.md)
- [Connect your advertiser account](docs/onboarding.md)
- [See what you can ask your agent](docs/use_cases.md)

## What your agent can do

- List publishers and compare publisher or campaign results.
- Look up sales, check their status and follow a validation job.
- Prepare approvals, declines or amendments for a batch of transactions.
- Preview offers, product feeds and conversion orders before sending them.

## What happens before live changes

Review the advertiser ID, the action, and the contents of the file the agent plans to send. For feeds, check the language and region. For conversion orders, check where Awin will send updates if you use a webhook. Keep a saved copy of the plan. The tool checks that the account, token, destination and file still match when it sends the request. [How to review a plan and receipt](docs/safety_model.md)

## What access this tool needs

Use an Awin API token and your advertiser ID. Awin limits advertiser API access by plan and account permissions. Enter the token in a private settings file. [Set up access](docs/onboarding.md)

## Install and first run

Ask your agent to install `awin-advertiser-safe-cli` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@awin-advertiser-safe-cli -g -y
```

The skill contains the guides and source for the Python command. [Install and run the command](docs/quickstart.md)

## Limits

Awin can take time to process a request. Check the receipt and the account before resending anything. For the changes this tool sends, recovery may require a separate change in Awin. [Commands and coverage](docs/api_coverage.md) · [Test results](docs/proof.md)

## Helpful docs

[All Awin Advertiser guides](docs/README.md)
