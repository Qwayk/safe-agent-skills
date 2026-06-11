# Command reference

Use this page when you need the exact WordPress command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--version`: show version (machine-readable in `--output json`)
- `--apply`: write changes (default is dry-run)
- `--output json|text`
- `--env-file PATH` (default: `.env`)
- `--config PATH` (optional; non-secret project defaults JSON)
- `--project-dir PATH` (optional; used for default output paths)
- `--log-file PATH` (audit JSONL)
- `--verbose` (HTTP logging)
- `--yes`: extra confirmation for batch jobs (required with `--apply`)
- `--plan-out PATH`: write a computed dry-run plan JSON to a file (v2; write-capable commands)
- `--receipt-out PATH`: write an apply receipt JSON to a file (v2; write-capable commands)

Notes:
- Global flags like `--apply`, `--output`, and `--env-file` must come **before** the subcommand (example: `wordpress-api-tool --apply media set ...`).
- In `--output json` mode, every invocation prints exactly one JSON object to stdout (including parse/usage/help/version flows).

## Auth

- `wordpress-api-tool auth check`

## Discover

- `wordpress-api-tool discover post-types [--include-raw] [--context view|edit]`
- `wordpress-api-tool discover statuses [--include-raw] [--context view|edit]`
- `wordpress-api-tool discover taxonomies [--include-raw] [--context view|edit]`

## Comments (read-only)

- `wordpress-api-tool comments list [--post-id ID] [--query "text"] [--status ...] [--author ID] [--parent ID] [--type ...] [--after ISO8601] [--before ISO8601] [--order asc|desc] [--orderby ...] [--limit 50] [--per-page N] [--max-pages 10] [--context view|edit]`
- `wordpress-api-tool comments get --id ID [--context view|edit]`

## Search (read-only)

- `wordpress-api-tool search query --query "text" [--type ...] [--subtype ...] [--limit 50] [--per-page N] [--max-pages 10]`

## Settings (read-only)

- `wordpress-api-tool settings get [--context view|edit]`

## Terms (read-only)

- `wordpress-api-tool terms list --taxonomy categories|tags [--query "text"] [--slug SLUG] [--hide-empty] [--limit 50] [--per-page N] [--max-pages 10] [--context view|edit]`
- `wordpress-api-tool terms get --taxonomy categories|tags --id ID [--context view|edit]`

## Users (read-only)

- `wordpress-api-tool users list [--query "text"] [--slug SLUG] [--limit 50] [--per-page N] [--max-pages 10] [--context view|edit]`
- `wordpress-api-tool users get --id ID [--context view|edit]`

## Post

- `wordpress-api-tool post find --query "text" [--post-type posts] [--limit 20]`
- `wordpress-api-tool post get --slug SLUG [--post-type posts] [--include-raw]`
- `wordpress-api-tool post truth (--slug SLUG | --id ID) [--post-type posts] [--resolve-urls]`
- `wordpress-api-tool post images --slug SLUG [--post-type posts] [--include-featured]`
- `wordpress-api-tool post set-image-captions --slug SLUG [--post-type posts|pages] [--caption ...|--caption-html ...|--captions-file captions.json] [--alt-text ...] [--only-ids 1,2,3] [--diff]`
- `wordpress-api-tool --apply post set-image-captions --slug SLUG ...`
- `wordpress-api-tool post replace-in-content (--slug SLUG | --id ID) --post-type posts --from "..." --to "..." --expected-count N [--max-replacements N] [--backup-out PATH] [--diff]`
- `wordpress-api-tool post replace-in-content (--slug SLUG | --id ID) --post-type posts|pages --from "..." --to "..." --expected-count N [--max-replacements N] [--backup-out PATH] [--diff]`
- `wordpress-api-tool --apply post replace-in-content ...` (requires `--backup-out`)
- `wordpress-api-tool post set-status (--slug SLUG | --id ID) --to publish [--require-current draft] [--post-type posts|pages]`
- `wordpress-api-tool --apply post set-status ...`
- `wordpress-api-tool post set-terms (--slug SLUG | --id ID) --set [--post-type posts] [--category-id ID] [--category-slug SLUG] [--clear-categories] [--tag-id ID] [--tag-slug SLUG] [--clear-tags]`
- `wordpress-api-tool --apply post set-terms ...`

Notes:
- `post set-image-captions` refuses if you provide none of `--caption/--caption-html/--alt-text`.
- `post set-image-captions` now saves the current post state under `.state/runs/<run-id>/before/` before apply. Use that saved file for a deliberate manual restore if needed.
- It only edits Gutenberg `wp:image` blocks where it can determine the attachment id (JSON attrs `id` or an `<img>` `wp-image-<id>` class). In per-id mapping mode (`--captions-file`), unidentifiable `wp:image` blocks are skipped.
- `post find` and `post get` query with `status=any` (includes drafts) when authenticated.
- `post set-status` refuses unless you provide exactly one selector (`--slug` or `--id`) and will refuse if `--require-current` doesn't match.
- `post set-status` now saves the current post state under `.state/runs/<run-id>/before/` before apply. The plan and receipt still show the previous status for a simple manual revert.
- `post set-status`, `post replace-in-content`, and `post set-image-captions` also support `--post-type pages`; when page mode is used, before-state paths and rollback notes still point to a `page.<command>` family entry.
- `post set-terms` requires `--set` (explicit replacement mode) and refuses if slug-based term resolution is missing or ambiguous.
- `post set-terms` replaces only the taxonomies you specify; if you provide only tags inputs, categories are left unchanged (and vice versa).
- `post set-terms` now saves the current post state under `.state/runs/<run-id>/before/` before apply. Use that saved file, or the shown previous term IDs, for a deliberate manual revert.
- If `post set-terms` fails verification after `--apply`, it exits non-zero and includes expected vs actual term IDs.
- `post replace-in-content` is an **exact string replacement** with strict guardrails: it refuses unless the `--from` string occurs exactly `--expected-count` times.
- `post replace-in-content` now saves the current post state under `.state/runs/<run-id>/before/` before apply.
- With `--apply`, `post replace-in-content` still requires `--backup-out` when you also want a dedicated content snapshot file outside the normal run-state folder.
  - Tip: to remove all occurrences, set `--max-replacements` to the same value as `--expected-count`.

## Media

- `wordpress-api-tool media find [--query "text"] [--limit 50] [--per-page N] [--max-pages 10] [--context view|edit]`
- `wordpress-api-tool media get --id 123`
- `wordpress-api-tool media resolve --url https://.../wp-content/uploads/...jpg`
- `wordpress-api-tool media download (--id 123 | --url https://...) [--out-dir <PROJECT_DIR>/cache/wp-media]`
- `wordpress-api-tool media download-batch --file items.csv [--out-dir <PROJECT_DIR>/cache/wp-media] [--skip-existing] [--max-items 500]`
- `wordpress-api-tool --apply --yes media download-batch --file items.csv ...`
- `wordpress-api-tool media set --id 123 [--caption ...] [--alt-text ...] [--title ...]`
- `wordpress-api-tool --apply media set --id 123 ...`
- `wordpress-api-tool media set-batch --file updates.json`
- `wordpress-api-tool --apply media set-batch --file updates.json`

`updates.json` can be either:
- an object mapping id to caption: `{"2264": "Caption ...", "2266": "Caption ..."}`
- or a list of update objects: `[{"id": 2264, "caption": "...", "alt_text": "...", "title": "..."}, ...]`

`items.csv` / `items.json` for `media download-batch` can be:
- CSV with headers `id,url,filename` (unknown columns ignored)
- JSON list: `[{"id": 123, "url": "https://...", "filename": "image.jpg"}, ...]`

Notes:
- `media set` refuses if you provide none of `--caption/--alt-text/--title`.
- `media download-batch` is dry-run by default; applying local file writes requires `--apply --yes`.
- `media set` now saves the current media item under `.state/runs/<run-id>/before/` before apply.
- `media set-batch` now saves the current target media rows under `.state/runs/<run-id>/before/` before apply.

## Jobs

- `wordpress-api-tool jobs run --file jobs.csv [--limit N]`
- `wordpress-api-tool --apply --yes jobs run --file jobs.csv ...` (currently blocked for safety until per-row before-state restore is added)

Notes:
- Jobs stop on the first error by default and return a non-zero exit code.
- `jobs run` dry-run is still available. Write mode is currently blocked with a clear refusal until per-row before-state restore is available. During dry-run, the plan includes a batch `before_state` entry for review.

## Migration

- `wordpress-api-tool migration tracking-from-xml --xml export.xml [--xml ...] [--out <PROJECT_DIR>/tracking.csv] [--append]`

Notes:
- The generated `tracking.csv` includes basic WordPress fields (`wp_post_id`, `wp_slug`, `wp_title`, `wp_status`, `wp_tags`, `wp_categories`, …) plus empty Ghost columns to fill as you perfect each post.
