# Plausible

Check how many people visited a site, which pages they read, where they came from and what they did. Ask for a short report or query one metric for a specific period.

A good first request is “Show me visits and pageviews for the last seven days, then list the top pages and traffic sources.”

## Install

Ask your agent to install the `plausible-api-safe-cli` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@plausible-api-safe-cli -g -y
```

Use the [quickstart](docs/quickstart.md) to connect a Stats API key and run your first traffic query. Plausible works with the hosted service and with self-hosted instances that expose the required API.

## Choose what to check

- [Read a weekly report or export CSV files](docs/reports.md).
- [Check a query file locally or run a custom query](docs/queries.md).
- [Find commands and flags](docs/command_reference.md), including site, goal and event commands.
- [Review a change before applying it](docs/safety_model.md). Site changes and test events need approval. Saved plans and receipts show what the tool checked.
- [See the supported API operations](docs/api_coverage.md) and [test results](docs/proof.md).
