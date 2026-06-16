# Authentication

Awin Advertiser authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because advertiser transactions, publisher checks, offers, product feeds, and conversion work can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Awin Advertiser environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

Required fields for `auth check`:

## Setup details

- `AWIN_API_TOKEN`
- `AWIN_ADVERTISER_ID`

`auth check` intentionally uses the advertiser publishers endpoint and sends:

- `Authorization: Bearer <AWIN_API_TOKEN>`
- `accessToken=<AWIN_API_TOKEN>` query param

Important notes for this tool:

- Authentication follows a strict endpoint map, not one universal auth rule.
- `auth check` is pinned to `GET /advertisers/{advertiserId}/publishers` and sends:
  - `Authorization: Bearer <AWIN_API_TOKEN>`
  - `accessToken=<AWIN_API_TOKEN>` query param
- For other advertiser commands, use the endpoint-specific mapping in:
  - `docs/references.md`
  - `docs/api_coverage.md`
- Conversion API examples use `x-api-key: <AWIN_API_TOKEN>` only.

For transaction batch validation specifically:

- `POST /advertisers/{advertiserId}/transactions/batch` is documented with both `Authorization` and an `accessToken` label in the batch header area.
- For transaction batch validation, send `Authorization: Bearer <AWIN_API_TOKEN>` plus `accessToken=<AWIN_API_TOKEN>` as a query parameter.
