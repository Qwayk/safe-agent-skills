# Authentication

GiantPanda access uses `GIANTPANDA_API_TOKEN`.

## Local readiness check

```bash
giantpanda auth check
```

This is read-only and local:

- it does not call GiantPanda,
- it only checks token presence and placeholder status,
- it never prints token values.

## Runtime authorization behavior

For API calls the tool uses:

- fixed host `https://account.giantpanda.com`
- `Authorization: Token <GIANTPANDA_API_TOKEN>`
- redirects disabled and refused, so the token-bearing request is not followed to another URL

## Error behavior

If token is missing or still a placeholder, read and write commands return `AuthenticationError` before any provider request:

- `giantpanda domains stats --start-date ... --end-date ...`
- `giantpanda domains add --apply ...`
