# API coverage (endpoints → CLI)

## Ghost Admin API

Summary:
- Provider: Ghost Admin API
- API base URL (default): `GHOST_ADMIN_API_URL` (must include `/ghost/api/admin/`)
- Auth method: Admin API key → JWT (`Authorization: Ghost <token>`)
- Versioning: `Accept-Version: <version>` (from `GHOST_ACCEPT_VERSION`)
- Last audited (UTC): 2026-06-01

Notes:
- Many commands are “transforms” that ultimately update a post/page payload via `PUT /posts/{id}/` or `PUT /pages/{id}/`.
- Writes are gated behind `--apply`. Destructive/bulk writes additionally require `--yes`.
- Snapshot-backed families write backup snapshots (before/after) under `backup-snapshots/` next to your `--env-file`.
- Write-capable commands also write per-run artifacts under `.state/runs/<run_id>/` (plan/receipt/audit).
- Recovery is mixed by family:
  - `snapshot_plus_restore`: direct update/edit families such as post/page patching and member/newsletter/tag/tier/offer updates.
  - `irreversible_and_clearly_labeled`: families that still cannot promise a direct restore path in plan output, including webhook, theme, image upload, jobs wrapper, and create/copy or resource-create families.
  - Several of those families are now dry-run-only because live apply requires explicit no-snapshot approval when no saved snapshot is available.

| Endpoint | Capability | CLI command family | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /site/` | Site info | `auth check --full-site` (and internal) | read-only | unit tests | Unauthenticated in Ghost; tool still sends auth headers consistently |
| `GET /posts/` | List posts | `post find`, link audits, exports | read-only | unit tests | Supports filters/limits |
| `GET /posts/slug/{slug}/` | Get post by slug | Most `post ... --slug` commands | read-only | unit tests | Read-before-write targeting by slug |
| `GET /posts/{id}/` | Get post by id | Most `post ... --id` commands | read-only | unit tests | Verification reads use id where possible |
| `POST /posts/` | Create post | `post create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST /posts/{id}/copy` | Copy post | `post copy` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /posts/{id}/` | Update post | `post patch`, `post set-status`, `post bodylex ...`, `post bodymob ...`, `post body ...` | write: `--apply` (some require `--yes`) | `docs/examples/*` + unit tests | Most direct edit flows are `snapshot_plus_restore`; publish-like email flows stay clearly labeled irreversible |
| `DELETE /posts/{id}/` | Delete post | `post delete` | write: `--apply --yes` | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /pages/` | List pages | `page find` | read-only | unit tests |  |
| `GET /pages/slug/{slug}/` | Get page by slug | `page get`, `page patch`, `page sync-md` | read-only | unit tests | Read-before-write targeting by slug |
| `POST /pages/` | Create page | `page create`, `page sync-md` | mixed: `page create` is requires explicit no-snapshot approval when no saved snapshot is available; `page sync-md` applies only when replacing an existing page | unit tests | Brand-new create applies require explicit no-snapshot approval when no saved snapshot is available |
| `POST /pages/{id}/copy` | Copy page | `page copy` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /pages/{id}/` | Update page | `page patch`, `page set-status`, `page sync-md` | write: `--apply` (some require `--yes`) | unit tests | Recovery: `snapshot_plus_restore` |
| `DELETE /pages/{id}/` | Delete page | `page delete` | write: `--apply --yes` | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /tags/` | List tags | `tag list`, `tag audit` | read-only | unit tests | Used for inventory/cleanup |
| `POST /tags/` | Create tag | `tag create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /tags/{id}/` | Update tag | `tag update` | write: `--apply` | unit tests | Recovery: `snapshot_plus_restore` |
| `DELETE /tags/{id}/` | Delete tags | `tag delete`, `tag delete-zero`, `tag merge` (optional) | write: `--apply --yes` | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /tiers/` | List tiers | `tier list` | read-only | unit tests | Supports `include` for prices/benefits |
| `GET /tiers/{id}/` | Get tier | `tier get` | read-only | unit tests |  |
| `POST /tiers/` | Create tier | `tier create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /tiers/{id}/` | Update tier | `tier update` | write: `--apply` | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /offers/` | List offers | `offer list` | read-only | unit tests |  |
| `GET /offers/{id}/` | Get offer | `offer get` | read-only | unit tests |  |
| `POST /offers/` | Create offer | `offer create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /offers/{id}/` | Update offer | `offer update` | write: `--apply` | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /members/` | List members | `member list`, exports | read-only | unit tests | Emails are redacted in output by default |
| `POST /members/` | Create member | `member create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /members/{id}/` | Update member | `member update` | write: `--apply` (some require `--yes`) | unit tests | Recovery: `snapshot_plus_restore` |
| `GET /newsletters/` | List newsletters | `newsletter list` | read-only | unit tests |  |
| `POST /newsletters/` | Create newsletter | `newsletter create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /newsletters/{id}/` | Update newsletter | `newsletter update` | write: `--apply` | unit tests | Recovery: `snapshot_plus_restore` |
| `POST /images/upload/` | Upload image | `image upload` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST /themes/upload` | Upload theme | `theme upload` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `PUT /themes/{name}/activate` | Activate theme | `theme activate` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available |
| `POST /webhooks/` | Create webhook | `webhook create` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available; proof stays ledger-based |
| `PUT /webhooks/{id}/` | Update webhook | `webhook update` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available; proof stays ledger-based |
| `DELETE /webhooks/{id}/` | Delete webhook | `webhook delete` | requires explicit no-snapshot approval when no saved snapshot is available | unit tests | Live apply requires explicit no-snapshot approval when no saved snapshot is available; proof stays ledger-based |

## Ghost Content API (read-only)

Summary:
- Provider: Ghost Content API
- API base URL (default): `GHOST_CONTENT_API_URL` (must include `/ghost/api/content/`)
- Auth method: Content API key via query param (`?key=...`)
- Versioning: `Accept-Version: <version>` (from `GHOST_ACCEPT_VERSION`)
- Last audited (UTC): 2026-06-01

Notes:
- This command family is read-only by design.
- Content API commands do not require Admin API credentials.

| Endpoint | Capability | CLI command family | Safety gates | Tests/examples | Notes |
|---|---|---|---|---|---|
| `GET /posts/` | Browse posts | `content posts list` | read-only | unit tests | Supports `filter`, `fields`, `include`, `order`, `limit`, `page`, `formats` |
| `GET /posts/{id}/` | Read post by id | `content posts get --id` | read-only | unit tests |  |
| `GET /posts/slug/{slug}/` | Read post by slug | `content posts get --slug` | read-only | unit tests |  |
| `GET /pages/` | Browse pages | `content pages list` | read-only | unit tests | Supports `filter`, `fields`, `include`, `order`, `limit`, `page`, `formats` |
| `GET /pages/{id}/` | Read page by id | `content pages get --id` | read-only | unit tests |  |
| `GET /pages/slug/{slug}/` | Read page by slug | `content pages get --slug` | read-only | unit tests |  |
| `GET /tags/` | Browse tags | `content tags list` | read-only | unit tests | Supports `filter`, `fields`, `include`, `order`, `limit`, `page` |
| `GET /tags/{id}/` | Read tag by id | `content tags get --id` | read-only | unit tests |  |
| `GET /tags/slug/{slug}/` | Read tag by slug | `content tags get --slug` | read-only | unit tests |  |
| `GET /authors/` | Browse authors | `content authors list` | read-only | unit tests | Supports `filter`, `fields`, `include`, `order`, `limit`, `page` |
| `GET /authors/{id}/` | Read author by id | `content authors get --id` | read-only | unit tests |  |
| `GET /authors/slug/{slug}/` | Read author by slug | `content authors get --slug` | read-only | unit tests |  |
| `GET /tiers/` | Browse tiers | `content tiers list` | read-only | unit tests | Supports `include`, `limit`, `page` |
| `GET /settings/` | Get settings | `content settings get` | read-only | unit tests | Does not accept query params beyond `key` |

## Known gaps (explicit)

This tool focuses on content/migration/editor workflows. It does not attempt to cover the full Ghost Admin API surface area.
If you need a capability that isn’t in `docs/command_reference.md`, add it deliberately and document it in this table.
