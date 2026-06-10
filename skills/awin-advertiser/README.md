# Awin Advertiser

Use this skill when you want your AI agent to review Awin advertiser activity, inspect publisher and transaction data, and prepare advertiser-side validation, offer, feed, or conversion work through explicit commands and review-first safety.

Install slug: `awin-advertiser`

## For non-technical users: Start here

- [What you can ask the agent to do](docs/use_cases.md)
- [Connect your Awin advertiser account](docs/onboarding.md)
- [How this skill stays safe](docs/safety_model.md)

Example requests you can ask the AI agent:

- "Show me which publishers drove results last month."
- "Check whether this Awin token is connected correctly before we do anything else."
- "Preview a batch of transaction approvals before applying them."
- "Prepare a product-feed upload safely and show me the proof files."
- "Create an offer draft and stop before anything goes live."

## What access this skill needs

- Most advertiser checks and advertiser-side updates use the normal Awin advertiser token.
- Conversion orders use the separate Awin Conversion API key.
- Live advertiser proof still depends on Awin advertiser API access being enabled for the account.

## What happens before live changes

- Publisher lookups, transaction checks, reports, and transaction-job status checks are read-only.
- Transaction batch validation, offers, product-feed uploads, and conversion orders start with a dry-run plan.
- Live apply requires explicit approval with the reviewed plan file.
- Irreversible sends stay explicit and leave a receipt.
- There is no raw request bridge.

## For technical users: Start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Configuration](docs/configuration.md)
- [Authentication](docs/authentication.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

## Verification note

The shipped Awin advertiser command families are implemented and locally tested in this skill folder. Live Awin advertiser proof is still pending because no real credentials are stored here and advertiser API access is still plan-gated.
