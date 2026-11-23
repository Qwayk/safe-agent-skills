# Dynadot

Check which domains expire soon, look up prices or availability, or see which nameservers a domain uses. You can also check incoming domain moves, orders, auctions, backorders, and marketplace listings.

Try asking, “List my active domains and flag anything that expires in the next 60 days.” Your agent can check the account and read the domain list before it proposes a change.

If you want to register, renew, or move a domain, or change its nameservers, your agent saves a plan for you to review first. For a move between Dynadot accounts, check both accounts and the receiver's Push Username. For a purchase, check the price before approving it.

## Install

Ask your agent to install the `dynadot-api-safe-cli` skill from the Qwayk catalog, or run:

```bash
npx skills add Qwayk/safe-agent-skills@dynadot-api-safe-cli -g -y
```

Use [Onboarding](docs/onboarding.md) to connect your account. Try [Quickstart](docs/quickstart.md) for domain checks and a nameserver plan.

## API version

The tool uses Dynadot API3. Dynadot plans to retire API3 and recommends its REST API. Its notice gives no shutdown date. See [what this tool covers](docs/api_coverage.md) and [Dynadot's notice](https://www.dynadot.com/domain/api-commands).

- [Find a command](docs/command_reference.md)
- [Review approvals and receipts](docs/safety_model.md)
- [See what we tested](docs/proof.md)
- [Browse the guides](docs/README.md)
