# References

These are the sources used to check coverage on April 27, 2026.

## Official Cloudflare docs used for the live audit

- API index: `https://developers.cloudflare.com/api/`
- API sitemap: `https://developers.cloudflare.com/api/sitemap-0.xml`
- Official method pages: `https://developers.cloudflare.com/api/resources/.../methods/.../`
- Make API calls: `https://developers.cloudflare.com/fundamentals/api/how-to/make-api-calls/`
- Create API tokens: `https://developers.cloudflare.com/fundamentals/api/get-started/create-token/`
- Account API tokens: `https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/`
- Token formats and the `cfat_` account-token prefix: `https://developers.cloudflare.com/fundamentals/api/get-started/token-formats/`
- Restrict API tokens: `https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/`
- API limits: `https://developers.cloudflare.com/fundamentals/api/reference/limits/`
- Browser Rendering / Browser Run overview: `https://developers.cloudflare.com/browser-rendering/`
- Browser Run quick actions: `https://developers.cloudflare.com/browser-rendering/browser-run/quick-actions/`

## Generated from those official docs

- [Saved API inventory used by the installed CLI](../src/cloudflare_api_tool/_data/live_official_api_inventory.json)
- [Operation list](api_coverage_live_official.md)

## Write and deployment checks

- [DNS record updates](https://developers.cloudflare.com/dns/manage-dns-records/how-to/batch-record-changes/) explains how a partial update keeps fields you leave out.
- [Worker deployments](https://developers.cloudflare.com/workers/versions-and-deployments/deployment-management/) explains how versions receive traffic.
- [Pages direct uploads](https://developers.cloudflare.com/pages/get-started/direct-upload/) explains production and preview uploads.

## Historical coverage

The per-area coverage records document earlier tool releases. Use the [current coverage ledger](api_coverage_live_official.md) for the operations available in this tool.
