# Settings (`/wp/v2/settings`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/settings/

Endpoint (core):
- `GET /wp/v2/settings`

Notes:
- This is often **admin-only** (capability-dependent).
- Some WordPress versions primarily support `context=edit` for settings responses.
- Treat this as an optional “snapshot” command: it may fail on low-privilege accounts and that’s expected.

