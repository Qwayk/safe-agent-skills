# Tags (`/wp/v2/tags`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/tags/

Endpoints (core):
- `GET /wp/v2/tags` (collection)
- `GET /wp/v2/tags/{id}` (single)

Common collection filters:
- `search` (text search)
- `slug` (exact match)
- `hide_empty=true` (exclude unused terms)

Pagination:
- `per_page` max 100
- headers: `X-WP-Total`, `X-WP-TotalPages`

