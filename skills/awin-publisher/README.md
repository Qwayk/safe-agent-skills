# Awin Publisher

See which advertiser programs you’ve joined, which offers you can use, and where your transactions came from. The tool can also generate tracking links and download an advertiser’s product feed to a file.

> List the publisher accounts my token can access. Then show me the programs I’ve joined in the account I choose.

Your agent checks the connection and confirms the publisher account first. It prepares a plan and waits for approval before submitting proof-of-purchase orders to Awin.

## Install and start

Ask your agent to install `awin-publisher-safe-cli` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@awin-publisher-safe-cli -g -y
```

[Install the CLI and run your first account check](docs/quickstart.md). The main Awin token handles account reads, reports, tracking links and enhanced feeds. Add a separate key only when you use legacy feeds or submit proof-of-purchase orders. [Set up access](docs/onboarding.md)

## What you can ask for

- Check program status, offers, and transaction queries.
- Review transactions or reports by advertiser, campaign, or creative.
- Generate tracking links and check your link quota.
- Download a feed to the file you choose. The enhanced feed must pass the file checks before it replaces a saved copy.
- Prepare an order submission and review its results after approval.

[Example requests](docs/use_cases.md) · [Commands](docs/command_reference.md) · [All guides](docs/README.md)

## Before submitting orders

For proof of purchase, Awin must enable the publisher and the advertiser must enable that program for the publisher. Show the publisher, advertiser, and exact orders before asking for approval. After a submission, check what Awin received and which orders are still pending. [Approval steps](docs/safety_model.md) · [Test results](docs/proof.md) · [API coverage](docs/api_coverage.md)
