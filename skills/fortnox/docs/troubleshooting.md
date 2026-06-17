# Troubleshooting

Start with the exact JSON error output, because it usually says whether Fortnox auth is missing, a token is expired, a required selector is unclear, or a safety approval is missing. The safest next check is to read the error, fix the missing value or target, and stop before retrying any command that could change invoices, bookkeeping, payroll, stock, or customer records.

A good first troubleshooting ask is: "Read this Fortnox JSON error output, explain the likely cause, and give me the safest next check without inventing missing data."

## Common issues

## No token found

If `auth check` says no access token is available:

1. Run `fortnox-api-tool auth token status`
2. If needed, run `fortnox-api-tool auth login`
3. Then run `fortnox-api-tool auth exchange-code --code <authorization_code> --state <state>`

## State mismatch

If `auth exchange-code` says the `--state` value does not match:

1. Run `fortnox-api-tool auth login` again
2. Use the new `state` value from that response
3. Retry the code exchange

## Expired token

If `auth check` says the token file looks expired:

```bash
fortnox-api-tool auth refresh
```

If you use service accounts instead of refresh tokens:

```bash
fortnox-api-tool auth service-account-token
```

## Service-account token blocked

If `auth service-account-token` fails:

- confirm `FORTNOX_SERVICE_TENANT_ID` is set
- confirm the first consent used `auth login --service-account`
- confirm the Fortnox app has service account enabled in the Developer Portal

## Debugging

- Use `--verbose` to see request start/end lines on stderr
- Use `--debug` for a Python stack trace
- Never paste tokens, client secrets, or Authorization headers into chat
