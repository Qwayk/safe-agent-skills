# Authentication

This tool uses a private API key from `.env`.

- `KLAVIYO_API_KEY`: used for `Authorization: Klaviyo-API-Key ...` on live calls.
- `KLAVIYO_COMPANY_ID`: optional, used for `/client/*` endpoints.

Run once to verify:

```bash
klaviyo-safe-agent-cli auth check
```

The check does not print secrets.
