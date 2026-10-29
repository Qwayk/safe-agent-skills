# ReservationService (Google Ads API v25)

Command shape:
- `google-ads-api-tool reservation-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `book-campaigns` — `ReservationService.BookCampaigns` (write; plan-first; unary_unary) — request: `BookCampaignsRequest` → response: `BookCampaignsResponse`
- `quote-campaigns` — `ReservationService.QuoteCampaigns` (write; plan-first; unary_unary) — request: `QuoteCampaignsRequest` → response: `QuoteCampaignsResponse`
