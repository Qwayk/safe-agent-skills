# Search (`/wp/v2/search`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/search-results/

Endpoint (core):
- `GET /wp/v2/search` (collection)

Common query parameters:
- `search` (query string)
- `type` (example: `post`, `term`) (site-dependent)
- `subtype` (example: `posts`, `pages`, `category`, `post_tag`) (site-dependent)

Pagination:
- `per_page` max 100
- headers: `X-WP-Total`, `X-WP-TotalPages`

Notes:
- Result objects typically include fields like `id`, `title`, `url`, `type`, and `subtype`.
- This endpoint is useful for migration targeting when you don’t know the exact post type or taxonomy ahead of time.

