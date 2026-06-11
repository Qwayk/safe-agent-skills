# API coverage (endpoints → CLI)

Summary:
- Provider: Unsplash
- API base URL: https://api.unsplash.com
- Auth method: Access Key via `Authorization: Client-ID ...` (no OAuth in this tool)
- Last audited (UTC): 2026-06-04

Notes:
- This tool sends `Accept-Version: v1` on all API requests.
- `GET /me` is not supported because it requires a Bearer token (OAuth), which is out of scope.
- Pagination: Unsplash docs state list endpoints are paginated with a default of 10 items, up to a maximum of 30 per page. This tool enforces `--per-page <= 30` consistently.

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes | Official docs |
|---|---|---|---|---|---|---|
| `GET /photos` | List photos | `unsplash-api-tool photos list`<br>`unsplash-api-tool export photos-list` | read-only API; local write: export writes JSON to `--out` (multi-page requires `--yes`) | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `order_by` | https://unsplash.com/documentation#list-photos |
| `GET /photos/:id` | Get a photo | `unsplash-api-tool photos get --id ...` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#get-a-photo |
| `GET /photos/random` | Random photo(s) | `unsplash-api-tool photos random` | read-only | `tests/test_unsplash_commands.py` | Supports `count`, `query`, `username`, `orientation`, `content_filter` | https://unsplash.com/documentation#get-a-random-photo |
| `GET /search/photos` | Search photos | `unsplash-api-tool photos search`<br>`unsplash-api-tool search photos`<br>`unsplash-api-tool export photos-search` | read-only API; local write: export writes JSON to `--out` (multi-page requires `--yes`) | `tests/test_unsplash_commands.py` | Supports `query`, `page`, `per_page` (max 30), optional `order_by` | https://unsplash.com/documentation#search-photos |
| `GET /photos/:id/statistics` | Photo stats | `unsplash-api-tool photos stats --id ...` | read-only | `tests/test_unsplash_commands.py` | Supports `resolution`, `quantity` | https://unsplash.com/documentation#get-a-photos-statistics |
| `GET /photos/:id/download` | Track a photo download (compliance) | `unsplash-api-tool photos download --id ...` | planned only; current apply requires explicit no-snapshot approval before this endpoint | `tests/test_unsplash_commands.py` + `docs/examples/*` | Optional local file write is also blocked in current apply | https://unsplash.com/documentation#track-a-photo-download |
| `GET /collections` | List collections | `unsplash-api-tool collections list` | read-only | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30) | https://unsplash.com/documentation#list-collections |
| `GET /collections/:id` | Get a collection | `unsplash-api-tool collections get --id ...` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#get-a-collection |
| `GET /collections/:id/photos` | List photos in a collection | `unsplash-api-tool collections photos --id ...`<br>`unsplash-api-tool export collections-photos --id ...` | read-only API; local write: export writes JSON to `--out` (multi-page requires `--yes`) | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `orientation` | https://unsplash.com/documentation#get-a-collections-photos |
| `GET /collections/:id/related` | Related collections | `unsplash-api-tool collections related --id ...` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#get-a-collections-related-collections |
| `GET /topics` | List topics | `unsplash-api-tool topics list` | read-only | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `order_by` | https://unsplash.com/documentation#list-topics |
| `GET /topics/:id` | Get a topic | `unsplash-api-tool topics get --id ...` | read-only | `tests/test_unsplash_commands.py` | `id` may be slug or id | https://unsplash.com/documentation#get-a-topic |
| `GET /topics/:id/photos` | List photos for a topic | `unsplash-api-tool topics photos --id ...`<br>`unsplash-api-tool export topics-photos --id ...` | read-only API; local write: export writes JSON to `--out` (multi-page requires `--yes`) | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `orientation` | https://unsplash.com/documentation#get-a-topics-photos |
| `GET /users/:username` | Get user profile | `unsplash-api-tool users get --username ...` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#get-a-users-profile |
| `GET /users/:username/photos` | List user photos | `unsplash-api-tool users photos --username ...`<br>`unsplash-api-tool export users-photos --username ...` | read-only API; local write: export writes JSON to `--out` (multi-page requires `--yes`) | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `order_by`, `orientation` | https://unsplash.com/documentation#list-a-users-photos |
| `GET /users/:username/likes` | List liked photos for a user | `unsplash-api-tool users likes --username ...` | read-only | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30), `order_by`, `orientation` | https://unsplash.com/documentation#list-a-users-liked-photos |
| `GET /users/:username/collections` | List user collections | `unsplash-api-tool users collections --username ...` | read-only | `tests/test_unsplash_commands.py` | Supports `page`, `per_page` (max 30) | https://unsplash.com/documentation#list-a-users-collections |
| `GET /users/:username/statistics` | User stats | `unsplash-api-tool users statistics --username ...` | read-only | `tests/test_unsplash_commands.py` | Supports `resolution`, `quantity` | https://unsplash.com/documentation#get-a-users-statistics |
| `GET /search/collections` | Search collections | `unsplash-api-tool search collections --query ...` | read-only | `tests/test_unsplash_commands.py` | Supports `query`, `page`, `per_page` (max 30) | https://unsplash.com/documentation#search-collections |
| `GET /search/users` | Search users | `unsplash-api-tool search users --query ...` | read-only | `tests/test_unsplash_commands.py` | Supports `query`, `page`, `per_page` (max 30) | https://unsplash.com/documentation#search-users |
| `GET /stats/total` | Global total stats | `unsplash-api-tool stats total` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#totals |
| `GET /stats/month` | Global monthly stats | `unsplash-api-tool stats month` | read-only | `tests/test_unsplash_commands.py` |  | https://unsplash.com/documentation#month |

## Known gaps (explicit)

- `GET /me` — requires OAuth Bearer token per official docs (out of scope for this issue).
- `POST /photos/:id/like` and `DELETE /photos/:id/like` — require OAuth Bearer token per official docs (out of scope).
