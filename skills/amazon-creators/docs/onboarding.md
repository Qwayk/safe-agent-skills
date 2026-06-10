# Onboarding

1. Open the Amazon Creators portal and create a Creators Catalog OAuth credential.
2. Copy the credential ID, secret, version, and partner tag into `.env` under `AMAZON_CREATORS_CREDENTIAL_ID`, `_SECRET`, `_VERSION`, and `_PARTNER_TAG`.
3. Set `AMAZON_CREATORS_LOCALE` to your marketplace (e.g., `en_US`). The tool uses this to pick the correct token endpoint and request headers.
4. Confirm the base URL is `https://creatorsapi.amazon/catalog/v1` (change `AMAZON_CREATORS_API_BASE_URL` if Amazon updates the hostname).
5. Use an existing `.state/token.json` when available. The token fetch/set helpers now plan and require approval before token endpoint use or token-cache writes when no saved snapshot is available.
6. Run `amazon-creators-api-tool auth check` to verify the creds and cached token.

The CLI’s `onboarding` command prints the steps above. If `.env` is missing, confirmed apply now requires explicit no-snapshot approval before creating it when no saved snapshot is available.

## What to ask your AI agent (examples)

- Show me the plan that spells out the locale, marketplace, and resources you intend to request before any live catalog call.
- Gather the classifications, technical info, and variation summary for an ASIN, and wait for my approval before fetching real data.
- List the supported locales first so the marketplace header aligns with the region I care about before we move forward.
- Treat the dry-run plan as your audit log and only release the actual browse-node hierarchy once I explicitly give the go-ahead.
