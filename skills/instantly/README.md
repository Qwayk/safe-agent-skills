# Instantly

See which cold email campaigns are running and which need attention. Check a campaign's status, replies and sending results before deciding what to change.

A good first request is “Show me my active campaigns and flag anything I should check before sending more.”

## Install

Ask your agent to install the `instantly-api-safe-cli` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@instantly-api-safe-cli -g -y
```

Follow the [quickstart](docs/quickstart.md) to check the CLI, connect with an Instantly API key and list your campaigns. Use a key with only the access the job needs.

## What you can do

- Check campaigns, sending accounts, leads and replies. Use analytics to see where results changed.
- Review lead lists, labels, tags, subsequences, webhooks and workspace settings.
- Preview changes before approving them. A campaign can start sending when you activate it. That takes a saved preview and explicit approval.

The [safety guide](docs/safety_model.md) explains which reads save private results to a local file, when a change needs extra approval, and how to read a receipt. The CLI saves a copy of the old settings where it can. Any repair is manual.

## Guides

- [What you can ask for](docs/use_cases.md)
- [Connect your account and fix setup problems](docs/onboarding.md)
- [Find a command](docs/command_reference.md), including [bulk lead imports](docs/command_reference.md#add-leads-in-bulk)
- [What the tool supports](docs/api_coverage.md)
- [What has been tested](docs/proof.md)
