# References

Last verified (UTC): `2026-06-04`

These are the official Google sources used for the current command surface, auth rules, and coverage ledger.

## Core Merchant docs

- Merchant API home: <https://developers.google.com/merchant/api>
- Merchant API overview: <https://developers.google.com/merchant/api/overview>
- Merchant REST reference index: <https://developers.google.com/merchant/api/reference/rest>
- Authorization overview: <https://developers.google.com/merchant/api/guides/authorization/overview>
- Access your own account with a service account: <https://developers.google.com/merchant/api/guides/authorization/access-your-account>
- Access client accounts with OAuth: <https://developers.google.com/merchant/api/guides/authorization/access-client-accounts>
- Migrate from `v1beta` to `v1`: <https://developers.google.com/merchant/api/guides/compatibility/migrate-v1beta-v1>

## Reference-only alpha methods used in this tool

- Loyalty customers `manage`: <https://developers.google.com/merchant/api/reference/rest/loyaltycustomers_v1alpha/accounts.loyaltyCustomers/manage>
- YouTube shopping checkout `applyOrderUpdate` (`v1alpha`): <https://developers.google.com/merchant/api/reference/rest/youtubeshoppingcheckout_v1alpha/accounts.orders/applyOrderUpdate>
- YouTube shopping checkout `applyOrderUpdate` (`v1beta`, accounted but not shipped): <https://developers.google.com/merchant/api/reference/rest/youtubeshoppingcheckout_v1beta/accounts.orders/applyOrderUpdate>

## Verification notes for the current ledger

- The REST reference index still publishes active `v1alpha` families such as `accounts_v1alpha`, `productstudio_v1alpha`, `reviews_v1alpha`, `youtube_v1alpha`, and `reports_v1alpha`.
- The REST reference index also still publishes `v1beta` families. This tool accounts for them in `docs/api_coverage.md` but does not ship them in the public CLI.
- On `2026-06-04`, the published discovery-document URLs for `loyaltycustomers_v1alpha`, `youtubeshoppingcheckout_v1alpha`, and `youtubeshoppingcheckout_v1beta` returned `404`, so those methods were reconciled directly from the official REST reference pages instead.
