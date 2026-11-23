# Sovrn test results

## November 23, 2026 local checks

Fresh CLI installs from the source and the local release copy each passed 33 tests with the network blocked. A separate skill install matched all 47 release files under `sovrn`.

The checks used simulated replies to run all three quickstart paths with only the required settings. They confirmed that the selected file supplied the key and publisher, links and errors hid the key, unreadable reports failed, and approved merchants showed which page was returned.

## August 12, 2026 checks

The Mac build of `0.1.0` passed 34 tests. On August 11, a live Commerce Link API check with a site key returned both eligible and ineligible links. A follow-up confirmed the CLI hid the key in the request and the optimized URL. Those results apply to the site whose key was used. Site approval and commission need their own checks.

This record includes no successful live examples for Commerce reports, the full approved-merchant list, comparisons, or Advertising.

## June 8, 2026 checks

The original local review checked version `0.1.0`, the settings check, and the command paths. The saved campaign example shows an invalid secret response from Sovrn. [Current smoke commands](quickstart.md)

## Example output

- [CLI version](examples/outputs/version.json)
- [Local settings check](examples/outputs/auth_check.json)
- [Commerce campaign request with an invalid secret](examples/outputs/commerce_campaigns_invalid_secret.json)

For any approved live check, use the matching key and a small request from the [command guide](command_reference.md). Review results privately before saving an example. Remove keys, private account IDs, tracking data, and business data that cannot be shared. [API coverage](api_coverage.md) lists the supported requests.
