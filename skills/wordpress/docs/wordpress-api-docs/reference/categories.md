# Categories (`/wp/v2/categories`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/categories/

Endpoints (core):
- `GET /wp/v2/categories` (collection)
- `GET /wp/v2/categories/{id}` (single)

Common collection filters:
- `search` (text search)
- `slug` (exact match)
- `hide_empty=true` (exclude unused terms)

Pagination:
- `per_page` max 100
- headers: `X-WP-Total`, `X-WP-TotalPages`

