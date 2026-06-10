# Quickstart

1. Copy `.env.example` → `.env` and fill the Amazon Creators credential fields:
   - `AMAZON_CREATORS_API_BASE_URL` (usually `https://creatorsapi.amazon/catalog/v1`).
   - `AMAZON_CREATORS_CREDENTIAL_ID`
   - `AMAZON_CREATORS_CREDENTIAL_SECRET`
   - `AMAZON_CREATORS_CREDENTIAL_VERSION` (use the documented ones, e.g., `2.1`, `2.2`, `2.3`, or `3.1`, `3.2`, `3.3`)
   - `AMAZON_CREATORS_LOCALE` (e.g., `en_US` or `en_GB`)
   - `AMAZON_CREATORS_PARTNER_TAG` (published with your credential; used for every catalog call)
   - `AMAZON_CREATORS_TIMEOUT_S` (optional; defaults to `30`)
   - `AMAZON_CREATORS_TOKEN_URL` (optional override for the token endpoint)
2. Run `amazon-creators-api-tool onboarding` to get the non-technical setup steps. If `.env` is missing, confirmed apply requires explicit no-snapshot approval before creating it when no saved snapshot is available.
3. Confirm the CLI runs: `amazon-creators-api-tool --output json --version`.
4. Use an existing cached token when available. `amazon-creators-api-tool --output json auth token fetch` now shows the blocked token-cache plan, and confirmed apply requires explicit no-snapshot approval before token endpoint use or cache writes.
   - Add `--force` if you need to bypass a valid cached token (for example, after rotating secrets).
   - `auth token set --file <token.json>` now shows the blocked token-cache plan.
5. Verify OAuth flow: `amazon-creators-api-tool auth check`.
6. Try the catalog commands to see the plan/apply loop:
   - Run `amazon-creators-api-tool items get --item-id B0EXAMPLE --resource-preset book-media` to output the dry-run `plan` without hitting Amazon.
   - Re-run with `--apply --include-raw` to call the API, view the simplified item summary, and produce a `receipt`/`receipt_out`.
