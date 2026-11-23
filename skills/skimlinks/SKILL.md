---
name: skimlinks
description: "Find Skimlinks merchants and offers, read publisher reports, look up product alternatives, and build affiliate links with skimlinks-safe-cli."
---

# Skimlinks

Use this skill for Skimlinks merchant search, publisher reports, Product Key lookups, and local Link Wrapper URLs. Use [the command guide](docs/command_reference.md) for the available commands.

For account reads, start with [setup](docs/onboarding.md) and run the sign-in check if the account is unverified. Keep credentials and settings files out of chat. Use the Publisher ID and domain that match the user's request. Keep the selected `--env-file` on each command when the user picked one.

If `has_more` is true, say that there are more merchants or offers. Ask Skimlinks for the next page when the user needs the full result. For reports, give the date range, the fields used, and what the results show. If a report reply is invalid, explain that it could not be read.

For Product Key, use the right publisher domain ID. The sign-in check only shows whether the credentials can get a token. Use a lookup to confirm Product Key access.

Build Link Wrapper URLs with the Site ID and full destination URL. Give the user the link to review. Leave it unopened. This action needs no account sign-in.

Use the named commands for reads. Data Pipe and Skimlinks JavaScript have separate setup guides and are outside the CLI. See [API coverage](docs/api_coverage.md) and [what was tested](docs/proof.md).
