# Skimlinks

Use this skill when you want your AI agent to inspect Skimlinks merchants, reports, Product Key lookups, and Link Wrapper URLs with explicit commands and no hidden endpoints.

Install slug: `skimlinks`

## For non-technical users: Start here

- [What you can ask the agent to do](docs/use_cases.md)
- [Connect your Skimlinks account](docs/onboarding.md)
- [How this skill stays safe](docs/safety_model.md)

Example requests you can ask the AI agent:

- "Find active Skimlinks merchants for this country and category."
- "Show me the top pages or links by commission for last month."
- "Check whether Product Key can return alternatives for these product URLs."
- "Build a Skimlinks Link Wrapper URL for this product link."

## What access this skill needs

- Merchant API and Reporting API need Skimlinks client credentials plus your publisher ID.
- Product Key may need separately enabled Product Key credentials.
- Product Key also needs a publisher domain ID.
- Link Wrapper needs a Link Wrapper ID and only builds the URL locally.

## What happens before live changes

- Merchant, Reporting, and Product Key commands are read or read-like only.
- Link Wrapper builds the official monetized URL locally and does not click it.
- There is no raw request bridge.
- Data Pipe and Skimlinks JavaScript are documented honestly, but they are not shipped as direct API command families here.

## For technical users: Start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Configuration](docs/configuration.md)
- [Authentication](docs/authentication.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

## Verification note

The explicit Skimlinks command families, Product Key publisher-domain checks, and Link Wrapper URL builder are implemented and locally tested in this skill folder. Live Skimlinks API proof is still pending because no real credentials are stored here.
