# Users (`/wp/v2/users`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/users/

Endpoints (core):
- `GET /wp/v2/users/me` (current authenticated user)
- `GET /wp/v2/users` (collection; often permission-restricted)
- `GET /wp/v2/users/{id}` (single; often permission-restricted)

Notes:
- Many sites restrict listing users to admins/editors (capability-dependent).
- The tool should treat `/users/me` as the most reliable low-privilege “auth smoke test”.
- Collection pagination and headers follow core patterns (`per_page`, `page`, `X-WP-Total`, `X-WP-TotalPages`).
- Useful collection filters:
  - `search` (text search)
  - `slug` (exact match)

