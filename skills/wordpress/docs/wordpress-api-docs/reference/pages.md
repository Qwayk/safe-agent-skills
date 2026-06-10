# Pages (`/wp/v2/pages`)

Last verified (UTC): 2026-01-27

Official docs:
- https://developer.wordpress.org/rest-api/reference/pages/

Notes:
- Pages behave like Posts for the core REST interface:
  - collection: `GET /wp/v2/pages`
  - single: `GET /wp/v2/pages/{id}`
  - update: `POST /wp/v2/pages/{id}`
- Pagination and headers match other collections (`per_page`, `page`, `X-WP-Total`, `X-WP-TotalPages`).

