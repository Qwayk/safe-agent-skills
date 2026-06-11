# References

Last updated (UTC): 2026-02-26

This tool is intentionally self-contained so it can be exported into its own repo
without relying on monorepo-only “vendored snapshot” paths.

Implementation defaults (base URL, API version, timeouts) are defined in:
- `src/meta_ads_api_tool/config.py`

Additional official references (used for general behavior, not copied verbatim):
- Marketing APIs overview: https://developers.facebook.com/docs/marketing-apis/
- Marketing API (overview): https://developers.facebook.com/docs/marketing-api/
- Marketing API Insights: https://developers.facebook.com/docs/marketing-api/insights
- Graph API overview: https://developers.facebook.com/docs/graph-api/
- Graph API versioning: https://developers.facebook.com/docs/graph-api/overview/versioning
- Access tokens overview: https://developers.facebook.com/docs/facebook-login/guides/access-tokens
- Graph API rate limiting: https://developers.facebook.com/docs/graph-api/overview/rate-limiting

Notes:
- Direct access to developers.facebook.com may be restricted in some environments. When in doubt, re-verify from a browser and update this file.
- This tool is read-only (GET-only) in this phase; do not infer write endpoints from these references.
