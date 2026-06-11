# References

Purpose:
- Record the exact sources behind the live coverage claim.
- Keep official Cloudflare docs ahead of vendored snapshots.

## Official Cloudflare docs used for the live audit

- API index: `https://developers.cloudflare.com/api/`
- API sitemap: `https://developers.cloudflare.com/api/sitemap-0.xml`
- Official method pages: `https://developers.cloudflare.com/api/resources/.../methods/.../`
- Make API calls: `https://developers.cloudflare.com/fundamentals/api/how-to/make-api-calls/`
- Create API tokens: `https://developers.cloudflare.com/fundamentals/api/get-started/create-token/`
- Restrict API tokens: `https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/`
- API limits: `https://developers.cloudflare.com/fundamentals/api/reference/limits/`
- Browser Rendering / Browser Run overview: `https://developers.cloudflare.com/browser-rendering/`
- Browser Run quick actions: `https://developers.cloudflare.com/browser-rendering/browser-run/quick-actions/`

## Generated from those official docs

- Live runtime allowlist: `docs/_generated/live_official_api_inventory.json`
- Live human ledger: `docs/api_coverage_live_official.md`
- Live coverage ledger: `docs/api_coverage_live_official.md`

## Historical inputs still kept in the repo

- `docs/cloudflare-api-docs/openapi.json`
- `docs/cloudflare-api-docs/extracts/`

These historical files are retained for old phase ledgers and audit history only.
They are not the active reference for the current live coverage claim.
