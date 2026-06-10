# API coverage (endpoints → CLI)

Last verified (UTC): 2026-01-28

This tool intentionally covers a small subset of the WordPress REST API, optimized for safe, deterministic migrations and metadata edits.

Summary:
- Provider: WordPress
- API base (default): `{WP_BASE_URL}/wp-json/wp/v2`
- Auth: Basic Auth using a WordPress Application Password (`WP_USERNAME`, `WP_APP_PASSWORD`)
- WordPress API writes: gated behind `--apply` (and batch jobs require `--apply --yes`)
- Local batch file writes: `media download-batch` requires `--apply --yes`
- v2 artifacts: `--plan-out` / `--receipt-out` for write-capable commands

## Scope and assumptions

- This report covers **core** WordPress endpoints (mostly in the `wp/v2` namespace) as documented in:
  - The vendored reference docs in this repo (`docs/wordpress-api-docs/`)
  - The official WordPress REST API docs on developer.wordpress.org
- WordPress REST API is **extensible** (plugins and themes can add endpoints). Those are out of scope for this tool unless we intentionally add support.
- This tool’s HTTP client is currently hard-coded to the `wp/v2` namespace (`{WP_BASE_URL}/wp-json/wp/v2`). Supporting other namespaces (example: `wp-site-health/v1`) would require explicit design work.

## Current CLI surface area (inventory)

From `docs/command_reference.md`:

- Auth: `auth check`
- Discover:
  - `discover post-types`
  - `discover statuses`
  - `discover taxonomies`
- Comments (read-only):
  - `comments list`
  - `comments get`
- Search (read-only): `search query`
- Settings (read-only): `settings get`
- Terms (read-only): `terms list`, `terms get`
- Users (read-only): `users list`, `users get`
- Posts/pages:
  - `post find` (use `--post-type posts|pages|...`)
  - `post get` (slug selector)
  - `post images` (extract referenced images + optionally featured image)
  - `post truth` (enriched view: author + terms + media, plus optional URL resolution)
  - `post set-image-captions` (Gutenberg `wp:image` blocks only; safe-by-default)
  - `post set-terms` (categories/tags; safe-by-default)
  - `post set-status` (high risk; safe-by-default)
- Media:
  - `media get`, `media resolve`, `media download`, `media download-batch`
  - `media find` (read-only)
  - `media set`, `media set-batch` (safe-by-default)
- Jobs: `jobs run` (batch runner; safe-by-default)
- Migration helpers (not REST API): `migration tracking-from-xml`

## Coverage table

| Endpoint | Capability | CLI command(s) | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /wp/v2/users/me` | Auth smoke test | `wordpress-api-tool auth check` | read-only | `docs/examples/outputs/auth_check.missing_env.json` | Requires valid Basic Auth; some hosts strip `Authorization` |
| `GET /wp/v2/types` | Discover post types | `wordpress-api-tool discover post-types` | read-only | unit tests | Use `--include-raw` to include full raw response |
| `GET /wp/v2/statuses` | Discover post statuses | `wordpress-api-tool discover statuses` | read-only | unit tests | Use `--include-raw` to include full raw response |
| `GET /wp/v2/taxonomies` | Discover taxonomies | `wordpress-api-tool discover taxonomies` | read-only | unit tests | Use `--include-raw` to include full raw response |
| `GET /wp/v2/comments` | List/filter comments | `wordpress-api-tool comments list` | read-only | unit tests | Defaults to `context=view` with pagination guardrails |
| `GET /wp/v2/comments/{id}` | Fetch comment by id | `wordpress-api-tool comments get --id ...` | read-only | unit tests | Defaults to `context=view` |
| `GET /wp/v2/search` | Search endpoint | `wordpress-api-tool search query --query ...` | read-only | unit tests | Pagination guardrails via `--limit/--max-pages` |
| `GET /wp/v2/settings` | Settings snapshot | `wordpress-api-tool settings get` | read-only | unit tests | Often requires admin capability; use `--context edit` if needed |
| `GET /wp/v2/categories` | List/search categories | `wordpress-api-tool terms list --taxonomy categories ...` | read-only | unit tests | Defaults to `context=view` with pagination guardrails |
| `GET /wp/v2/categories/{id}` | Fetch category by id | `wordpress-api-tool terms get --taxonomy categories --id ...` | read-only | unit tests | Defaults to `context=view` |
| `GET /wp/v2/tags` | List/search tags | `wordpress-api-tool terms list --taxonomy tags ...` | read-only | unit tests | Defaults to `context=view` with pagination guardrails |
| `GET /wp/v2/tags/{id}` | Fetch tag by id | `wordpress-api-tool terms get --taxonomy tags --id ...` | read-only | unit tests | Defaults to `context=view` |
| `GET /wp/v2/users` | List/search users | `wordpress-api-tool users list ...` | read-only | unit tests | Often permission-restricted; defaults to `context=view` |
| `GET /wp/v2/users/{id}` | Fetch user by id | `wordpress-api-tool users get --id ...` | read-only | unit tests | Often permission-restricted; defaults to `context=view` |
| `GET /wp/v2/{post_type}?search=...` | Search posts/pages | `wordpress-api-tool post find --query ...` | read-only | `docs/examples/outputs/usage_error.post_find.json` | `post_type` defaults to posts |
| `GET /wp/v2/{post_type}?slug=...` | Fetch by slug | `post get`, `post truth`, `post images` | read-only | unit tests | Used as read-before-write targeting for slug-based write commands |
| `GET /wp/v2/{post_type}/{id}` | Fetch by id | `post truth` and verification reads | read-only | unit tests | Used for verification after writes when id is known |
| `POST /wp/v2/{post_type}/{id}` | Update post body captions (Gutenberg `wp:image`) | `post set-image-captions` | write: requires `--apply` | `tests/test_v2_plan_receipt_exports.py` + `docs/examples/*` | Verification is idempotence (re-run yields zero changes) |
| `POST /wp/v2/{post_type}/{id}` | Set categories/tags (taxonomy terms) | `post set-terms` | write: requires `--apply` | `tests/test_post_set_terms.py` | Slug inputs resolve via `GET /tags?slug=...` / `GET /categories?slug=...`; refuses on missing/ambiguous; verification is read-back set equality |
| `POST /wp/v2/{post_type}/{id}` | Change post status (high risk) | `post set-status` | write: requires `--apply` | `tests/test_v2_plan_receipt_exports.py` | Prefer `--require-current` to avoid accidental publishing |
| `GET /wp/v2/media/{id}` | Get media | `media get`, `media download`, `media download-batch` | read-only | unit tests | `media download` writes a local file; `media download-batch` can resolve ids to `source_url` |
| `GET /wp/v2/media` | Search/list media | `media find` | read-only | unit tests | Uses `?search=...` when `--query` is provided; pagination guardrails; defaults to `context=view` |
| `GET /wp/v2/media?include=...` | Fetch media list by IDs | internal for `post images`, `post truth`, `media set-batch` | read-only | unit tests | Used to hydrate attachment IDs into Media objects; also used for read-before-write verification |
| `GET /wp/v2/media?search=...` | Search media (best-effort) | `media resolve` (internal search) | read-only | unit tests | Used to resolve a media item by `source_url` via filename search; refuses on ambiguity |
| `POST /wp/v2/media/{id}` | Update media fields | `media set` | write: requires `--apply` | `tests/test_v2_plan_receipt_exports.py` | Verification is a read-back compare of requested fields |
| `POST /wp/v2/media/{id}` (repeated) | Batch media updates | `media set-batch --file ...` | write: requires `--apply --yes` | `tests/test_v2_plan_receipt_exports.py` | Stops on first error |
| `GET /wp/v2/users/{id}` | Fetch author details | internal for `post truth` | read-only | unit tests | Used to enrich `post truth` output (best-effort; failures are tolerated) |
| `GET /wp/v2/tags?include=...` | Fetch tag names by IDs | internal for `post truth` | read-only | unit tests | Used to enrich `post truth` output |
| `GET /wp/v2/categories?include=...` | Fetch category names by IDs | internal for `post truth` | read-only | unit tests | Used to enrich `post truth` output |

## Endpoints used (high-level)

- [x] `GET /wp/v2/users/me` → `auth check`
- [x] `GET /wp/v2/types` → `discover post-types`
- [x] `GET /wp/v2/statuses` → `discover statuses`
- [x] `GET /wp/v2/taxonomies` → `discover taxonomies`
- [x] `GET /wp/v2/comments` → `comments list`
- [x] `GET /wp/v2/comments/{id}` → `comments get`
- [x] `GET /wp/v2/search` → `search query`
- [x] `GET /wp/v2/settings` → `settings get`
- [x] `GET /wp/v2/categories` → `terms list --taxonomy categories`
- [x] `GET /wp/v2/categories?slug=...` → `post set-terms` (term slug resolution)
- [x] `GET /wp/v2/categories/{id}` → `terms get --taxonomy categories`
- [x] `GET /wp/v2/tags` → `terms list --taxonomy tags`
- [x] `GET /wp/v2/tags?slug=...` → `post set-terms` (term slug resolution)
- [x] `GET /wp/v2/tags/{id}` → `terms get --taxonomy tags`
- [x] `GET /wp/v2/users` → `users list`
- [x] `GET /wp/v2/users/{id}` → `users get`
- [x] `GET /wp/v2/{post_type}?search=...` → `post find`
- [x] `GET /wp/v2/{post_type}?slug=...` → `post get`, `post truth`, `post images`, write commands that target by slug
- [x] `GET /wp/v2/{post_type}/{id}` → `post truth`, write commands that target by id, verification reads
- [x] `POST /wp/v2/{post_type}/{id}` → `post set-image-captions` (write; `--apply` required)
- [x] `POST /wp/v2/{post_type}/{id}` → `post set-terms` (write; `--apply` required; categories/tags only)
- [x] `POST /wp/v2/{post_type}/{id}` → `post set-status` (write; `--apply` required; status changes are high risk)
- [x] `GET /wp/v2/media/{id}` → `media get`, `media download`, `media download-batch`, `media set` (read-before-write), verification reads
- [x] `GET /wp/v2/media?search=...` → `media find`
- [x] `GET /wp/v2/media?include=...` → `post images`, `post truth`, `media set-batch`
- [x] `GET /wp/v2/media?search=...` → `media resolve` (best-effort resolver; used by `post truth --resolve-urls`)
- [x] `POST /wp/v2/media/{id}` → `media set` (write; `--apply` required)
- [x] `POST /wp/v2/media/{id}` (repeated) → `media set-batch` (write; `--apply` required)
- [x] `GET /wp/v2/users/{id}` → `post truth` (author enrichment)
- [x] `GET /wp/v2/tags?include=...` → `post truth` (term name enrichment)
- [x] `GET /wp/v2/categories?include=...` → `post truth` (term name enrichment)

## Gaps (what WordPress core supports that this tool does not yet)

This is a best-effort gap list against the vendored core reference docs in `docs/wordpress-api-docs/reference/`.

High-value reads (good next expansions):

- Media beyond “by id/resolve”: advanced bulk download workflows (resume, integrity checks, metadata export) (`media.md`)

Later / advanced (often site-specific, higher risk, or more moving parts):

- Revisions (`post-revisions.md`, `page-revisions.md`, `block-revisions.md`, etc.)
- Menus and navigation (`nav_menus.md`, `nav_menu_items.md`, `menu-locations.md`, `wp_navigations.md`, …)
- Blocks/patterns/templates/global styles (`blocks.md`, `block-types.md`, `block-patterns.md`, `wp_templates.md`, `wp_global_styles.md`, …)
- Themes/plugins endpoints (`themes.md`, `plugins.md`) (high-risk operational surface)

## References (official + vendored)

Vendored (preferred offline references in this repo):

- Posts: `docs/wordpress-api-docs/reference/posts.md`
- Pages: `docs/wordpress-api-docs/reference/pages.md`
- Media: `docs/wordpress-api-docs/reference/media.md`
- Users: `docs/wordpress-api-docs/reference/users.md`
- Application Passwords: `docs/wordpress-api-docs/reference/application-passwords.md`
- Comments: `docs/wordpress-api-docs/reference/comments.md`
- Search: `docs/wordpress-api-docs/reference/search.md`
- Settings: `docs/wordpress-api-docs/reference/settings.md`
- Categories: `docs/wordpress-api-docs/reference/categories.md`
- Tags: `docs/wordpress-api-docs/reference/tags.md`

Official (online):

- REST API handbook: https://developer.wordpress.org/rest-api/
- Posts reference: https://developer.wordpress.org/rest-api/reference/posts/
- Pages reference: https://developer.wordpress.org/rest-api/reference/pages/
- Media reference: https://developer.wordpress.org/rest-api/reference/media/
- Users reference: https://developer.wordpress.org/rest-api/reference/users/
- Comments reference: https://developer.wordpress.org/rest-api/reference/comments/
- Search reference: https://developer.wordpress.org/rest-api/reference/search-results/
- Settings reference: https://developer.wordpress.org/rest-api/reference/settings/
- Categories reference: https://developer.wordpress.org/rest-api/reference/categories/
- Tags reference: https://developer.wordpress.org/rest-api/reference/tags/

## Behaviors and tests

- [x] Strict JSON output contract (exactly one JSON object to stdout in `--output json`, including parse/usage/help/version flows) → `src/wordpress_api_tool/cli.py`, `tests/test_cli_json_output_contract.py`
- [x] Dry-run by default for write-capable commands (`--apply` required) → `src/wordpress_api_tool/cli.py`, `src/wordpress_api_tool/commands/`
- [x] v2 plan/receipt exports (`--plan-out` / `--receipt-out`) for write-capable commands → `src/wordpress_api_tool/v2.py`, `tests/test_v2_plan_receipt_exports.py`
- [x] Batch jobs support dry-run review under `--plan-out`; write mode is currently blocked (`--apply`) until per-row before-state restore is added
- [x] Batch local media downloads require `--apply --yes` and stop on first error → `src/wordpress_api_tool/commands/media.py`, `tests/test_media_download_batch.py`
- [x] Verification after write:
  - Media updates: re-fetch and compare requested fields → `src/wordpress_api_tool/commands/media.py`
  - Post-body edits: verify by idempotence (re-running yields no further changes) → `src/wordpress_api_tool/commands/post.py`
