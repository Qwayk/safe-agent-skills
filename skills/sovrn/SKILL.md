---
name: sovrn
description: Check affiliate links and read Sovrn Commerce and Advertising reports with the site's or publisher's matching key.
---

# Sovrn

Use this skill to check whether a product link can earn, see which pages or merchants are earning, or read advertising results. Start with the user's site or publisher and date range.

Run `sovrn-safe-cli --env-file .env onboarding` if the settings file needs to be created. Keep the same `--env-file` for the rest of the work. Run `auth check` to see which settings are present. Then make the smallest relevant request to confirm access.

- A Commerce site API key checks links and asks for bids or product suggestions.
- A Commerce secret key reads campaigns, approved merchants, and Commerce reports.
- Coupons and price comparisons use both Commerce keys.
- Advertising reports use the Advertising key and publisher ID.

Use the named commands in the command guide. The tool reads reports and requests estimates or suggestions. For browser code, MCP, or publishing work, tell the user where that work belongs.

In the answer, show the account or site, dates, filters, and what the provider returned. Tell the user if you only checked one page or if the report failed. Keep keys and private report details out of shared messages.

[Quickstart](docs/quickstart.md) · [Command guide](docs/command_reference.md)
