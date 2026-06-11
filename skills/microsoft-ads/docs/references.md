# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: Microsoft Advertising API (Microsoft Ads) v13
- API docs home: https://learn.microsoft.com/en-us/advertising/
- Get started: https://learn.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13
- Web service addresses (SOAP endpoints + WSDL discovery; prod + sandbox): https://learn.microsoft.com/en-us/advertising/guides/web-service-addresses?view=bingads-13
- OAuth (auth code + refresh token): https://learn.microsoft.com/en-us/advertising/guides/authentication-oauth?view=bingads-13
- Developer token and account/permissions overview: https://learn.microsoft.com/en-us/advertising/guides/account-hierarchy-permissions?view=bingads-13
- Service operations indexes (v13):
  - Campaign Management: https://learn.microsoft.com/en-us/advertising/campaign-management-service/campaign-management-service-operations?view=bingads-13
  - Bulk: https://learn.microsoft.com/en-us/advertising/bulk-service/bulk-service-operations?view=bingads-13
  - Reporting: https://learn.microsoft.com/en-us/advertising/reporting-service/reporting-service-operations?view=bingads-13
  - Ad Insight: https://learn.microsoft.com/en-us/advertising/ad-insight-service/ad-insight-service-operations?view=bingads-13
  - Customer Management: https://learn.microsoft.com/en-us/advertising/customer-management-service/customer-management-service-operations?view=bingads-13
- Last verified (UTC): 2026-03-04

## Other sources (only if needed)

- (none)
