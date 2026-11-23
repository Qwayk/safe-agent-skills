# Porkbun

Use this tool to check domain prices, see which domains expire soon, or review DNS in your Porkbun account. It can also read nameservers, URL forwarding, balances, marketplace listings and webhook deliveries, and save SSL files privately.

Try asking your agent, “Show me the current .com registration, renewal and transfer prices,” or “Show me the DNS records for example.com.”

Before a change, the tool saves a plan for you to review. For example, you can ask it to change how long a DNS answer can be cached. When you approve, the tool checks that the same Porkbun keys are in use and that the record still matches what you reviewed. It checks Porkbun again after the change.

## Install

Ask your agent to install the `porkbun` skill from the Qwayk catalog, or run:

```bash
npx skills add Qwayk/safe-agent-skills@porkbun -g -y
```

Use [Onboarding](docs/onboarding.md) to connect your account and [Quickstart](docs/quickstart.md) for your first read or planned change. Keep your API keys in a private env file or environment variables.

## What you can do

The tool has 66 named commands for the 53 paths in its pinned Porkbun API spec. There are 39 reads and 27 writes. Registration, renewal and transfer require approval to spend. Registration also requires agreement to Porkbun's terms.

- [Find a command](docs/command_reference.md)
- [Review approvals and receipts](docs/safety_model.md)
- [See what we tested offline](docs/proof.md)
- [Browse all docs](docs/README.md)
