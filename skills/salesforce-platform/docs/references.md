# References

## Official Salesforce sources used

- Salesforce REST API Developer Guide PDF
  - <https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_rest.pdf>
- Salesforce Bulk API 2.0 and Bulk API Developer Guide PDF
  - <https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_asynch.pdf>
- Create Actions from Named Query API
  - <https://developer.salesforce.com/docs/ai/agentforce/guide/agent-namedquery.html>
- Accessing Object Data with Salesforce Platform APIs
  - <https://developer.salesforce.com/blogs/2024/04/accessing-object-data-with-salesforce-platform-apis>

Last verified (UTC): `2026-05-26`

## Implementation note

The runtime scope was mapped against official Salesforce PDF snapshots downloaded on `2026-05-26` and locally verified as API version `67.0` for both the REST guide and the Bulk API 2.0 guide.

The public search index for the canonical REST PDF still showed a `66.0` snippet on `2026-05-26`. The downloaded official PDFs were treated as the fresher source. That is an inference from the official documents available on the same day.

## Main doc areas used

- REST guide resource table and reference chapter for scope boundaries
- REST guide chapters for:
  - queries and search
  - recently viewed records
  - blob upload and blob download
  - event-series delete
  - support knowledge
  - list views
  - quick actions
  - composite resources
  - OpenAPI document generation for sObjects (Beta)
- Bulk guide sections for:
  - ingest job create, upload, close, list, abort, delete, and result downloads
  - query job create, list, abort, delete, result downloads, and result pages
