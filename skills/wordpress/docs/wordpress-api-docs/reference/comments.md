# Comments (`/wp/v2/comments`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/comments/

Endpoints (core):
- `GET /wp/v2/comments` (collection)
- `GET /wp/v2/comments/{id}` (single)

Useful collection filters (common):
- `post` (filter by post/page id)
- `search` (text search)
- `status` (example values: `approve`, `hold`, `spam`, `trash`)
- `author` (user id)
- `parent` (comment id)
- `type` (comment type)
- date filters: `after`, `before` (ISO8601)

Pagination:
- `per_page` max 100
- headers: `X-WP-Total`, `X-WP-TotalPages`

Permissions:
- What a user can see depends on capabilities and the comment status (approved vs pending/spam/trash).
- `context=view` is the safest default.

