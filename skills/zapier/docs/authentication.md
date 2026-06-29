# Authentication

The tool uses environment values from `.env`.

- `ZAPIER_ACCESS_TOKEN` is the primary auth token (`Authorization: Bearer ...`).
- `ZAPIER_CLIENT_ID` + `ZAPIER_CLIENT_SECRET` are supported fallback credentials where the API requires client auth.
- `ZAPIER_JWT` supports JWT-based auth when your integration uses that flow.

Run:

```bash
qwayk-zapier-safe-agent-cli --output json auth check
```

No command prints token values. If auth is missing, the tool returns a structured validation error.
