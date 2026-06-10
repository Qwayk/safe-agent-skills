# Media (`/wp/v2/media`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/media/

Endpoints (core):
- `GET /wp/v2/media` (collection)
- `GET /wp/v2/media/{id}` (single)
- `POST /wp/v2/media/{id}` (update; write)

Common patterns:
- Collection search uses `search=...` (filename/title-ish depending on host/theme/plugins).
- Bulk “lookup by IDs” uses `include=1,2,3` with `per_page` sized appropriately.
- Pagination headers: `X-WP-Total`, `X-WP-TotalPages`.

Security/permissions:
- `context=view` is safest/lowest privilege.
- `context=edit` may be required to see raw fields and is usually permission-restricted.

