# Amazon Creators

Install slug: `amazon-creators`

Use this skill when you want your AI agent to review Amazon Creators catalog data for books and media formats, with dry-run-first catalog requests and explicit approval before local token or env helper writes.

The shipped surface covers the audited public Creators Catalog scope from Issue #404: `browse-nodes describe`, `items get`, `variations get`, `search`, and locale helpers that expand high-level resource presets into Amazon's concrete resource enums.

## For non-technical users: start here

- [What you can do](docs/use_cases.md)
- [Connect your Amazon Creators account](docs/onboarding.md)
- [How live work stays safer](docs/safety_model.md)

## For technical users: start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof pack](docs/proof.md)
- [Docs index](docs/README.md)

## What the review flow looks like

- Catalog commands default to a dry-run plan so you can preview locale, resources, and parameters before anything touches the live API.
- The follow-up confirmed run returns a receipt plus the simplified data your agent asked for.
- Local env and token helpers also plan first, and they require explicit no-snapshot approval before local file writes or token endpoint use when no saved before-state exists.

## Example requests

- "Look up this ISBN or ASIN and summarize the available media formats."
- "Search Amazon Creators for these book keywords and compare the best matches."
- "Show me which locales and resource presets this tool already supports."
