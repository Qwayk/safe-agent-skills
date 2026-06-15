# Authentication

Awin Publisher authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because publisher reporting, link building, feeds, and proof-of-purchase workflows can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Awin Publisher environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Setup details

- `AWIN_API_TOKEN`: core publisher API token for accounts, programs, offers, transactions, reports, and linkbuilder.
- `AWIN_FEED_API_KEY`: legacy product feed list and legacy feed download helper.
- `AWIN_PROOF_OF_PURCHASE_API_KEY`: proof-of-purchase order submission only.

## Core publisher API

Most publisher API commands send:

- `Authorization: Bearer <token>`
- `accessToken=<token>` query parameter

Important exception:

- `feeds enhanced-download` uses Bearer auth only, matching the official enhanced feed page.

## Legacy feeds

Legacy feed access uses the feed API key in the URL on the legacy feed host.

## Proof of purchase

Proof-of-purchase order submission uses:

- `x-api-key: <api key>`

It does not use the bearer token flow.
The official proof-of-purchase page also says live use needs Awin-side publisher enablement and advertiser-side CLO enablement.

## Smoke check

```bash
awin-publisher-safe-cli --output json auth check
```

Secrets are never printed in tool output, including failing HTTP error paths.
