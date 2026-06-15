# Authentication

Dynadot authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because domains, DNS, auctions, backorders, transfers, and account checks can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Dynadot environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

You store it locally in your `.env` file (gitignored).

Notes:

## Setup details

- The Dynadot API key is sent as a **URL query parameter** (`key=...`), so URLs must be treated as sensitive.
- This tool redacts `key=...` anywhere it might appear in logs or errors.
