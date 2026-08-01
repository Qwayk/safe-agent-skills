# Engineering notes

The operation registry is pinned to the supplied official OpenAPI file. Keep `operations.py`, the parser surface, tests, and `api_coverage.md` at 40 total operations, 38 stable commands, and two local HTTP-501 refusals.

Path values are percent-encoded as one segment before they are joined to the fixed base. Empty HTTP 204 responses are successful with `result: null`. HTTP 202 responses preserve `spaceship-async-operationid` and use `accepted_not_completed`.

Transport calls set `allow_redirects=False`. Pagination validates `take` and `skip` before network: 100 is the shared safe default for domain, SellerHub, sold-domain, and SafePay lists, while DNS allows up to 500. Sold-domain continuation uses the official `cursor` field and preserves both official sale-date filters.

Write plans compare a canonical request-body digest instead of saving raw private bodies. Contact IDs and SafePay transaction IDs use canonical digests in selectors and persisted command displays; billing contact IDs are masked. Opaque private-data errors are stored only as redacted digests, including nested `detail`, `message`, response, and raw fallbacks. `transferRequest` snapshots `getTransferInfo`. Reliable readback uses the reviewed domain for `domainCreate`, response `contactId` for contact writes, request `name` for SellerHub creation, and response `transactionId` for SafePay creation. Missing IDs and checkout-link creation remain `unverified`; HTTP 202 never triggers immediate readback.

`runs.py` accepts only non-empty, single-segment run IDs. It validates the resolved run directory before creating `.state/runs/<run_id>/`, so a run ID cannot redirect automatic plans, receipts, audits, or summaries outside the runs directory.

Retained starter modules are not connected to the parser and are excluded from sdist and wheel. Keep the installed surface limited to the fixed operation registry and necessary local front doors.
