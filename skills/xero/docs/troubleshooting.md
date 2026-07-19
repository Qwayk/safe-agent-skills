# Troubleshooting

The CLI returns one JSON error object by default. It should say what is missing without printing the credential or private provider response.

## No local token

```bash
qwayk-xero-safe-agent-cli auth status --profile pkce
```

If `exists` is false, repeat `auth start` and `auth exchange`. If the refresh token is present but the access token expired, run `auth refresh`.

## OAuth state or code rejected

- The returned state must exactly match the state from the current authorization URL.
- Saved PKCE state expires after 15 minutes.
- The authorization code file must contain only one code and must stay local.
- The redirect URI must exactly match both the Xero app and `.env`.

## No tenant selected

Run `tenant list`, then `tenant select` with an ID from that live result and the correct region. Do not copy a tenant ID from another app or credential.

For a Custom Connection, run `tenant custom-discover` and use global `--auth-profile custom` on the fixed command.

## Missing scope

Run `inventory show --command exact.command` to see the minimum scope. PKCE scopes are additive, so run a new `auth start` for the command and authorize again. Do not replace a granular scope with a broader deprecated scope unless the catalog marks that exact compatibility need and you deliberately use `--allow-deprecated-scope`.

## Wrong region or gated access

Payroll commands are limited to their AU, NZ, or UK family. eInvoicing and tax-report listing/detail are AU/NZ only; the 1099 report is US-only; CIS settings are UK-only. Bank Feeds, Finance, journals, Payment Services, eInvoicing, payroll, Projects, Practice Manager, Xero HQ, Xero Tax, and App Store functions can also need a product, partner status, payment, certification, role, tier, security review, or commercial access.

## App Store billing command unavailable

Treat the four `app-store.*` commands as legacy XASS transition access, not as a new billing setup. Xero deprecated XASS in March 2026, accepted no new apps after 4 December 2025, and required existing customers to migrate by 1 July 2026. The endpoints remain documented, but only Xero can confirm whether a legacy app is still entitled to call them. Do not replace the App Store profile with another token after an access failure.

## A write refuses to apply

Read the error and the saved plan. Common reasons are a missing approval, no-snapshot acknowledgement, changed tenant, changed catalog, changed input, changed target snapshot, or modified plan integrity. Create a new plan instead of editing a saved plan by hand.

## Rate limit or provider error

Read requests use bounded retries for 429 and transient server statuses and respect `Retry-After`. Writes are not automatically retried. The receipt and safe output include documented rate-limit headers when Xero sends them.

Use `--verbose` only for safe request timing on stderr. It does not print headers or bodies.
