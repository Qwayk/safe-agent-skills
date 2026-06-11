# References (sources)

## Official Awin source pages used by this tool

Last verified (UTC): 2026-06-09

- API overview / plan access context
  - `Awin's APIs overview` - https://help.awin.com/advertisers/docs/en/awins-apis-overview
  - `Introduction` - https://help.awin.com/apidocs/introduction-1
  - `For Advertisers` - https://help.awin.com/apidocs/for-advertisers
- Authentication
  - `Authentication` - https://help.awin.com/apidocs/api-authentication
- Advertiser publishers
  - `Get Publisher Information` - https://help.awin.com/apidocs/get-publishers-information-for-advertiser
- Advertiser transactions list
  - `Get List of Transactions` - https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-advertiser
- Advertiser transactions by ids
  - `Get List of Transactions by id's` - https://help.awin.com/apidocs/returns-a-list-of-transactions-for-a-given-advertiser-by-ids
- Advertiser batch validation
  - `Validate Transactions` - https://help.awin.com/apidocs/approve-decline-amend-batch-transactions-for-a-given-advertiser
- Advertiser transaction jobs
  - `Get Validation Status` - https://help.awin.com/apidocs/check-the-status-of-the-validation-batch-job
  - `Get Transaction Details` - https://help.awin.com/apidocs/check-the-status-of-validation-batch-job-with-transactions-details
- Publisher performance report
  - `Get Publisher Performance` - https://help.awin.com/apidocs/get-publisher-performance-report
- Campaign performance report
  - `Get Campaign Performance` - https://help.awin.com/apidocs/get-campaign-data-for-advertiser-report
- Offers API
  - `Post Offers` - https://help.awin.com/apidocs/offers-api
- Product feed upload
  - `Post Product Feed (Google Format)` - https://help.awin.com/apidocs/retail-advertiser-productapidocumentation
- Conversion API
  - `Conversion API` - https://help.awin.com/apidocs/conversion-api

## Provider

- Provider: Awin Advertiser API
- Base URL: `https://api.awin.com`
- API reference: Awin API docs published by the platform (entry URL in tool environment)

## Auth mapping by endpoint (this tool)

- `GET /advertisers/{advertiserId}/transactions/`
- `GET /advertisers/{advertiserId}/transactions`
- `GET /advertisers/{advertiserId}/reports/publisher`
- `GET /advertisers/{advertiserId}/reports/campaign`
- `GET /advertisers/{advertiserId}/publishers`

  - `Authorization: Bearer <AWIN_API_TOKEN>`
  - `accessToken=<AWIN_API_TOKEN>` query parameter

- `POST /advertisers/{advertiserId}/transactions/batch`

  - `Authorization: Bearer <AWIN_API_TOKEN>` (required by non-conversion rules)
  - `accessToken=<AWIN_API_TOKEN>` query parameter was used by this tool for deterministic parity with other non-conversion transaction flows.
  - Note: the public batch page currently shows `Authorization` and a stray `accessToken` entry in the header-parameters area. To keep behavior deterministic, this implementation treats access token as query token as well.

- `GET /advertisers/{advertiserId}/transactions/jobs`
- `GET /advertisers/{advertiserId}/transactions/jobs/{jobId}`
  - `Authorization: Bearer <AWIN_API_TOKEN>` only

- `POST /promotion/advertiser/{advertiser_id}`
- `POST /advertisers/{ADVERTISER_ID}/awinfeeds/{VERTICAL}/{LOCALE}/products`
  - `Authorization: Bearer <AWIN_API_TOKEN>` (no `accessToken` query parameter shown in fetched docs)

- `POST /s2s/advertiser/{advertiser_id}/orders`
  - `x-api-key: <AWIN_API_TOKEN>` only
  - dry-run by default in CLI

## Source-use note

- Only official Awin docs were used for this tool mapping and the auth notes above.
