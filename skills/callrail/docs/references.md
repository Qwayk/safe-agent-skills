# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: CallRail
- API docs home: `https://apidocs.callrail.com/`
- Auth docs: `https://support.callrail.com/hc/en-us/articles/5711821845389-CallRail-s-API-documentation`
- API keys and token model: `https://support.callrail.com/hc/en-us/articles/5711821845389-CallRail-s-API-documentation`
- Rate limits docs: `https://apidocs.callrail.com/`
- Query-shaping reference used for the current CLI surface: CallRail API sections for Authorization, Offset Pagination, Relative Pagination, Sorting, Filtering, and Field Selection on `https://apidocs.callrail.com/`
- Latest audit focus: rechecked API-key auth wording, read-only-by-default key behavior, single-resource field selection, the paginated read-query sections behind `docs/api_coverage.md`, and the REST-only parser boundary after the helper-command removal
- Last verified (UTC): `2026-06-06`

## Other sources (only if needed)

- No other sources required for this tool snapshot.
