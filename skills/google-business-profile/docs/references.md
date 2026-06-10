# References

Purpose:
- Keep the official Google source set behind the Google Business Profile coverage claim.
- Record which source type we rely on for each API family before broad implementation starts.

## Rules

- Never include secrets in this file.
- Prefer official Google docs and official Google discovery documents only.
- When docs disagree, keep both sources listed and record the mismatch in `docs/api_coverage.md`.

## Coverage boundary sources

- Docs home: https://developers.google.com/my-business
- Reference overview: https://developers.google.com/my-business/ref_overview
- Content overview: https://developers.google.com/my-business/content/overview
- Basic setup: https://developers.google.com/my-business/content/basic-setup
- Legacy Google My Business REST reference: https://developers.google.com/my-business/reference/rest
- Last verified (UTC): 2026-06-04

## Family sources

- Account Management API
  - REST docs: https://developers.google.com/my-business/reference/accountmanagement/rest
  - Discovery: https://mybusinessaccountmanagement.googleapis.com/$discovery/rest?version=v1

- Business Information API
  - REST docs: https://developers.google.com/my-business/reference/businessinformation/rest
  - Discovery: https://mybusinessbusinessinformation.googleapis.com/$discovery/rest?version=v1

- Business Calls API
  - REST docs: https://developers.google.com/my-business/reference/businesscalls/rest
  - Discovery URL documented by Google: https://mybusinessbusinesscalls.googleapis.com/$discovery/rest?version=v1

- Lodging API
  - REST docs: https://developers.google.com/my-business/reference/lodging/rest
  - Discovery: https://mybusinesslodging.googleapis.com/$discovery/rest?version=v1

- Media upload v1
  - Method page: https://developers.google.com/my-business/reference/rest/v1/media/upload
  - Upload flow docs: https://developers.google.com/my-business/content/upload-photos

- Notifications API
  - REST docs: https://developers.google.com/my-business/reference/notifications/rest
  - Discovery: https://mybusinessnotifications.googleapis.com/$discovery/rest?version=v1

- Performance API
  - REST docs: https://developers.google.com/my-business/reference/performance/rest
  - Discovery: https://businessprofileperformance.googleapis.com/$discovery/rest?version=v1

- Place Actions API
  - REST docs: https://developers.google.com/my-business/reference/placeactions/rest
  - Discovery: https://mybusinessplaceactions.googleapis.com/$discovery/rest?version=v1

- Q&A API
  - REST docs: https://developers.google.com/my-business/reference/qanda/rest
  - Change log: https://developers.google.com/my-business/content/qanda/change-log
  - Discovery: https://mybusinessqanda.googleapis.com/$discovery/rest?version=v1

- Verifications API
  - REST docs: https://developers.google.com/my-business/reference/verifications/rest
  - Discovery: https://mybusinessverifications.googleapis.com/$discovery/rest?version=v1

## Notes

- The official docs describe Google Business Profile as a federated API family. Newer specialized APIs and the legacy `v4.9` surface must both be accounted for.
- Some families are clearly approval-gated or role-gated in Google’s docs. The coverage claim must stay honest about that even when commands are implemented.
