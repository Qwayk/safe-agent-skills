# Posts (`/wp/v2/posts`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/posts/

Endpoints (core):
- `GET /wp/v2/posts` (collection)
- `GET /wp/v2/posts/{id}` (single)
- `POST /wp/v2/posts/{id}` (update; write)

Notes (for safe tooling):
- Collections are paginated (`per_page` max 100, `page` starting at 1).
- Pagination headers on collections:
  - `X-WP-Total`: total items
  - `X-WP-TotalPages`: total pages
- Useful collection filters for migration/discovery:
  - `search` (full-text search)
  - `slug` (exact match)
  - `status` (WordPress defaults collections to `publish`; use `status=any` when authenticated and you need drafts)
- `context`:
  - `view` is safest/lowest privilege
  - `edit` exposes additional fields and often requires higher capabilities

