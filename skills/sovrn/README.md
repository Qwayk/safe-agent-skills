# Sovrn

Use this skill when you want your AI agent to inspect the official Sovrn Commerce APIs and Sovrn Advertising Reporting APIs through explicit read-only commands.

Install slug: `sovrn`

## For non-technical users: Start here

- [What you can ask the agent to do](docs/use_cases.md)
- [Connect your Sovrn account](docs/onboarding.md)
- [How this skill stays safe](docs/safety_model.md)

Example requests you can ask the AI agent:

- "Check my Sovrn campaigns and tell me which ones look active."
- "Show me page or transaction report data for yesterday."
- "Build an affiliate link check for this product URL."
- "Recommend products for this article draft."
- "Pull the advertising account report for this date range."

## What access this skill needs

- Commerce campaigns, reports, and merchant-group commands use your Sovrn Commerce secret key.
- Links and product recommendation commands use the Sovrn Commerce site API key.
- Some Commerce command families use both pieces depending on the endpoint.
- Advertising reports need the Sovrn Advertising API key plus the publisher ID.

## What happens before live changes

- This skill is read-only today, even when an official endpoint uses `POST`.
- It does not invent raw requests, browser-only flows, or MCP beta coverage.
- `auth check` is a local setup check. Real vendor proof comes from the shipped read commands.

## For technical users: Start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Configuration](docs/configuration.md)
- [Authentication](docs/authentication.md)
- [API coverage](docs/api_coverage.md)
- [Proof and verification](docs/proof.md)

## Verification note

The shipped Sovrn Commerce and Advertising read commands are implemented and locally tested in this skill folder. Positive live Sovrn proof is still pending because no real credentials are stored here.
