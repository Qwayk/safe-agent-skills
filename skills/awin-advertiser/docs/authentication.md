# Authentication

This tool uses `.env` credentials directly.

Required fields for `auth check`:

- `AWIN_API_TOKEN`
- `AWIN_ADVERTISER_ID`

`auth check` intentionally uses the advertiser publishers endpoint and sends:

- `Authorization: Bearer <AWIN_API_TOKEN>`
- `accessToken=<AWIN_API_TOKEN>` query param

Important notes for this tool:

- The tool uses a strict endpoint map, not one universal auth rule.
- `auth check` is pinned to `GET /advertisers/{advertiserId}/publishers` and sends:
  - `Authorization: Bearer <AWIN_API_TOKEN>`
  - `accessToken=<AWIN_API_TOKEN>` query param
- For other advertiser commands, use the endpoint-specific mapping in:
  - `docs/references.md`
  - `docs/api_coverage.md`
- Conversion API examples use `x-api-key: <AWIN_API_TOKEN>` only.

For transaction batch validation specifically:

- `POST /advertisers/{advertiserId}/transactions/batch` is documented with both `Authorization` and an `accessToken` label in the batch header area.
- This tool uses a deterministic choice: `Authorization: Bearer <AWIN_API_TOKEN>` plus `accessToken=<AWIN_API_TOKEN>` as a query parameter.
