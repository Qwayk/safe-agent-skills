# Awin Publisher

Use this skill when you want your AI agent to review Awin publisher accounts, joined programs, offers, transactions, reports, feeds, linkbuilder tasks, and proof-of-purchase uploads with explicit commands and review-first safety.

Install slug: `awin-publisher`

## For non-technical users: Start here

- [What you can ask the agent to do](docs/use_cases.md)
- [Connect your Awin publisher account](docs/onboarding.md)
- [How this skill stays safe](docs/safety_model.md)

Example requests you can ask the AI agent:

- "Check which Awin publisher accounts this token can use."
- "List joined programs for this publisher account."
- "Pull yesterday's approved transactions."
- "Generate a tracking link for this advertiser."
- "Download the enhanced retail feed for this advertiser."
- "Prepare a proof-of-purchase upload for review before sending it."

## What access this skill needs

- Most publisher reads use your Awin API token.
- Legacy feed downloads use the separate legacy feed key.
- Proof-of-purchase order uploads use the separate proof-of-purchase API key.
- Live proof-of-purchase also depends on Awin-side publisher enablement and advertiser-side CLO enablement.

## What happens before live changes

- Accounts, programs, offers, transactions, reports, linkbuilder, and most feed work stay read-only or download-only.
- `proof-of-purchase orders create` starts with a dry-run plan.
- A live upload only happens after explicit approval with a reviewed plan file.
- There is no raw request bridge.

## For technical users: Start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Configuration](docs/configuration.md)
- [Authentication](docs/authentication.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

## Verification note

The shipped Awin publisher command families are implemented and locally tested in this skill folder. Live Awin proof is still pending because no real credentials are stored here.
