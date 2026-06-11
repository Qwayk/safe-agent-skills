# Command reference

Use this page when you need the exact Freepik command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## `auth`
- `freepik-api-tool auth check`

## `search`
- `freepik-api-tool search images --query TEXT [--limit N] [--page N] [--param k=v ...] [--exclude-ai]`
- `freepik-api-tool search photos --query TEXT [--limit N] [--page N] [--param k=v ...] [--exclude-ai]`

Optional output helpers (both `images` and `photos`):
- `--shortlist` (emit a compact, stable JSON object for human selection)
- `--write-jobs PATH` (write a jobs CSV compatible with `jobs run`; local-only file output)
- `--job-format FMT` (default: `jpg`)
- `--job-image-size SIZE` (optional; example: `2000px`)
- `--write-jobs` output is local-only; remove local files manually if no longer needed.

Shortlist output schema (stable keys; item fields may be `null` when Freepik omits them):
- Top-level:
  - `ok` (boolean)
  - `mode` (string; `search_shortlist`)
  - `query` (string)
  - `page` (number)
  - `limit` (number)
  - `count` (number; number of items in `items`)
  - `items` (array of objects)
  - `jobs_csv` (object; only present when `--write-jobs` is used)
- Each `items[]` object:
  - `id` (string|null)
  - `title` (string|null)
  - `preview_url` (string|null)
  - `license_url` (string|null)
  - `author` (string|null)
  - `orientation` (string|null)
  - `resource_url` (string|null)
- `jobs_csv` object (when present):
  - `path` (string)
  - `rows` (number)
  - `columns` (array of strings)

Notes:
- Freepik uses `filters` as a `deepObject` query param. Pass nested filters using bracket syntax, e.g.:
  - `--param 'filters[license][freemium]=1'` (free resources)
  - `--param 'filters[license][premium]=1'` (premium resources, requires premium access)
  - `--param 'filters[orientation]=horizontal'`
  - (AI filtering is not reliably supported by the API; use `--exclude-ai` + manual review)

Important: some `filters` keys are arrays. For example, `content_type` must be an array:
- ✅ `--param 'filters[content_type][]=photo'`
- ❌ `--param 'filters[content_type]=photo'` (the API rejects this with HTTP 400)

`search photos` defaults:
- Adds `filters[content_type][]=photo` unless overridden by your `--param`.

`--exclude-ai`:
- Runs an additional per-item `resource get` call and filters out results when the resource detail indicates AI via `is_ai_generated=true` or `has_prompt=true`.
- This is slower (extra API calls) but is the only way for the tool to enforce AI filtering because the browse response does not include AI flags.

Pricing note:
- Freepik API pricing is per operation and can change. Freepik’s pricing page lists separate prices for search and for downloads.
- It does not clearly state how “resource detail” requests are billed; assume any request may count.

## `resource`
- `freepik-api-tool resource get --id ID`
- `freepik-api-tool resource related --id ID [--limit N]`
- `freepik-api-tool resource shoot-pack --id ID [--limit N] [--same-series] [--same-collection] [--same-author] [--suggested] [--write-jobs PATH] [--job-format FMT] [--job-image-size SIZE]`

## `preview`
- `freepik-api-tool preview --id ID [--save-preview DIR]`

Notes:
- Without `--save-preview`, preview output only returns the URL.
- `--save-preview` writes local preview files only and requires manual cleanup if you want to remove them.

## `download`
Dry-run by default. Licensed live download also needs `--ack-no-snapshot` because no saved before-state snapshot is available for this write family.

- Safety: refuses unless the resource detail explicitly includes `is_ai_generated=false` AND `has_prompt=false`.
- `freepik-api-tool download --id ID --format FMT [--out-dir DIR] [--inventory PATH] [--post-slug SLUG] [--ghost-id ID] [--usage-role featured|body] [--image-size SIZE] [--download-url-jsonpath P] [--license-url-jsonpath P] [--force]`

Approved single-download example:

```bash
freepik-api-tool --apply --ack-no-snapshot download --id ID --format jpg --out-dir downloads --inventory licensed-downloads-ledger.csv
```

Notes:
- `--out-dir` and `--inventory` can be provided via `--config` using `downloads_dir` and `inventory_csv`.
- `--image-size` is only supported by Freepik on the `/download` endpoint (no-format). Approved apply still needs explicit no-snapshot approval before reaching that endpoint.
- `--post-slug/--ghost-id/--usage-role` are optional metadata fields for the inventory CSV.
- Dry-run output includes `preview_url`, `resource_url`, and `no_snapshot_available` before-state metadata so you can visually sanity-check the approved ID before live download.
- Approved apply writes the file and inventory row, then returns `rows`, `no_snapshot_approval`, `verification`, and `recovery`.
- If you omit `--ack-no-snapshot`, the tool refuses before the licensed download endpoint, file write, or inventory row write.

## `jobs`
Batch downloads require `--apply --yes`, and licensed download rows also need `--ack-no-snapshot`.

- `freepik-api-tool jobs run --file jobs.csv [--out-dir DIR] [--inventory PATH] [--limit N]`

Approved batch example:

```bash
freepik-api-tool --apply --yes --ack-no-snapshot jobs run --file jobs.csv --out-dir downloads --inventory licensed-downloads-ledger.csv
```

Notes:
- `--out-dir` and `--inventory` can be provided via `--config` using `downloads_dir` and `inventory_csv`.
- `jobs run` emits a single JSON summary.
- Licensed download rows require explicit no-snapshot approval. Approved rows write the local file and inventory row, while missing approval returns a refusal.
- `jobs run` includes a `recovery` block with `strategy=no_inverse`, `rollback_ready=false`, and `automatic_rollback=false`.
- Remote licensed writes are not reversible in this CLI. Local cleanup for helper files is manual.

Job CSV columns:
- `resource_id` (or `id`)
- `format`
- optional `image_size` (e.g. `2000px`)
- optional `post_slug`
- optional `ghost_id`
- optional `usage_role` (`featured` or `body`)
- optional `force` (`true/false`)
- optional `download_url_jsonpath`
- optional `license_url_jsonpath`
