# Authentication

Merchant API and Reporting API use the same Skimlinks temporary-token flow.

The CLI sends a POST request to:

```text
https://authentication.skimapis.com/access_token
```

The request body follows the official docs:

```json
{
  "client_id": "from .env",
  "client_secret": "from .env",
  "grant_type": "client_credentials"
}
```

The CLI never prints `client_secret` or `access_token`.

## Product Key Access

The official Product Key docs say usual credentials may not work and Product Key is available upon request. The CLI supports separate Product Key credentials:

- `SKIMLINKS_PRODUCT_CLIENT_ID`
- `SKIMLINKS_PRODUCT_CLIENT_SECRET`

If those are blank, Product Key commands can fall back to the shared credentials, but the command output and docs must stay honest that Skimlinks may still block Product Key access.

Product Key also requires a publisher domain ID. Set `SKIMLINKS_PUBLISHER_DOMAIN_ID` in `.env` or pass `--publisher-domain-id` on each Product Key command.

## Link Wrapper Access

Link Wrapper does not use the temporary-token flow. It needs the domain-specific ID shown by Skimlinks and uses it as the `id` query parameter.
