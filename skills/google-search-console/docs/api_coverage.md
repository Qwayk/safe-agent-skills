# API coverage (Discovery methods → CLI)

Purpose:
- Make “100% coverage” measurable (no guessing about what’s implemented).
- Pin the canonical inventory to a committed discovery snapshot.

## Summary

- Provider: Google Search Console API v1
- Base URL (default): `https://searchconsole.googleapis.com/`
- Auth: Installed-app OAuth (recommended) or service account JSON
- Pinned discovery snapshot: `docs/official_discovery_searchconsole_v1_2026-03-05.json`
- Total methods in snapshot: **11**
- Last audited (UTC): 2026-03-05

## Inventory mapping (100% of snapshot)

Naming rule:
- Use `method.id` from the discovery snapshot.
- Drop the first segment (service prefix), then split by `.`, convert each segment from camelCase to kebab-case.

| Discovery method id | HTTP | Path | CLI command | Safety gates |
|---|---:|---|---|---|
| `searchconsole.urlInspection.index.inspect` | POST | `v1/urlInspection/index:inspect` | `gsc-api-tool url-inspection index inspect --body-json '{"inspectionUrl":"https://example.com/","siteUrl":"sc-domain:example.com"}'` | Read-like POST (no `--apply`) |
| `searchconsole.urlTestingTools.mobileFriendlyTest.run` | POST | `v1/urlTestingTools/mobileFriendlyTest:run` | `gsc-api-tool url-testing-tools mobile-friendly-test run --body-json '{"url":"https://example.com/"}'` | Read-like POST (no `--apply`) |
| `webmasters.searchanalytics.query` | POST | `webmasters/v3/sites/{siteUrl}/searchAnalytics/query` | `gsc-api-tool searchanalytics query --site-url https://example.com/ --body-json '{"startDate":"2026-03-01","endDate":"2026-03-05","dimensions":["query"]}'` | Read-like POST (no `--apply`) |
| `webmasters.sitemaps.delete` | DELETE | `webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}` | `gsc-api-tool sitemaps delete --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` | Delete requires `--apply --yes --ack-irreversible --plan-in` |
| `webmasters.sitemaps.get` | GET | `webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}` | `gsc-api-tool sitemaps get --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` | Read-only |
| `webmasters.sitemaps.list` | GET | `webmasters/v3/sites/{siteUrl}/sitemaps` | `gsc-api-tool sitemaps list --site-url https://example.com/` | Read-only |
| `webmasters.sitemaps.submit` | PUT | `webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}` | `gsc-api-tool sitemaps submit --site-url https://example.com/ --feedpath https://example.com/sitemap.xml` | Write requires `--apply` (dry-run plan by default) |
| `webmasters.sites.add` | PUT | `webmasters/v3/sites/{siteUrl}` | `gsc-api-tool sites add --site-url https://example.com/` | Write requires `--apply` (dry-run plan by default) |
| `webmasters.sites.delete` | DELETE | `webmasters/v3/sites/{siteUrl}` | `gsc-api-tool sites delete --site-url https://example.com/` | Delete requires `--apply --yes --ack-irreversible --plan-in` |
| `webmasters.sites.get` | GET | `webmasters/v3/sites/{siteUrl}` | `gsc-api-tool sites get --site-url https://example.com/` | Read-only |
| `webmasters.sites.list` | GET | `webmasters/v3/sites` | `gsc-api-tool sites list` | Read-only |

## Known gaps

None (by definition: this tool’s command surface is generated from the pinned discovery snapshot and enforced in unit tests).
