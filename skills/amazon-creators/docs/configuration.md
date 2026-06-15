# Configuration

Amazon Creators configuration is the local setup an agent needs before it can check creator lists, storefront details, and creator-campaign reporting. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Amazon Creators values are required, which ones are optional, and confirm the setup without showing secrets."

## Where settings come from

The tool reads keys from `.env` (or any file passed via `--env-file`). Only non-secret config goes into `--config`.

Required env vars:

- `AMAZON_CREATORS_API_BASE_URL`: base API URL, typically `https://creatorsapi.amazon/catalog/v1`.
- `AMAZON_CREATORS_CREDENTIAL_ID`: OAuth credential ID (from the Amazon Creators portal).
- `AMAZON_CREATORS_CREDENTIAL_SECRET`: OAuth credential secret (never log or commit this).
- `AMAZON_CREATORS_CREDENTIAL_VERSION`: credential version string (e.g., `2` or `3`).
- `AMAZON_CREATORS_LOCALE`: marketplace locale (e.g., `en_US`, `en_GB`, `de_DE`); used for token selection and request headers.
- `AMAZON_CREATORS_PARTNER_TAG`: the partner tag tied to your credential; every catalog request includes it in the payload (`partnerTag`) while the `x-marketplace` header is derived from the locale/marketplace selection.
- `AMAZON_CREATORS_CREDENTIAL_VERSION` should match the documented flavors (`2.1`, `2.2`, `2.3` for the Cognito endpoints and `3.1`, `3.2`, `3.3` for Login With Amazon). The tool automatically picks the correct token URL.

Optional env vars:

- `AMAZON_CREATORS_TIMEOUT_S` (default 30 seconds).
- `AMAZON_CREATORS_TOKEN_URL`: override for the token endpoint if Amazon rotates URLs.

If a value is missing, the tool refuses with a clear message (no secrets leaked).
