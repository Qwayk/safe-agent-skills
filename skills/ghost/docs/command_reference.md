# Command reference

Use this page when you need the exact Ghost command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--apply`: write changes (default is dry-run)
- `--yes`: extra confirmation for destructive actions, status changes, and batch jobs
- `--ack-irreversible`: extra acknowledgement for irreversible actions (example: actions that can trigger email delivery)
- `--ack-theme-change`: extra acknowledgement for theme activation (high-impact)
- `--ack-no-verify`: acknowledge that verification may not be possible (example: webhooks; Ghost has no get/list endpoint)
- `--env-file PATH` (default: `.env`)
- `--timeout-s N`
- `--verbose` (HTTP request start/end lines)
- `--output json|text`
- `--log-file PATH` (audit JSONL; secrets redacted)
- `--plan-out PATH`: write computed plan JSON to a file (v2)
- `--plan-in PATH`: apply only if recomputed plan matches this file (v2 drift detection; required for high/irreversible applies)
- `--receipt-out PATH`: write receipt JSON after apply (v2)
- `--run-id ID`: override run id used for artifacts/history
- `--artifacts-dir DIR`: override run artifacts directory
- `--no-artifacts`: disable writing `.state/runs/` artifacts/history

Backups:
- Snapshot-backed write families save JSON snapshots under `backup-snapshots/` next to your `--env-file` (by domain + date).

Recovery contracts:
- `snapshot_plus_restore`: snapshot-backed updates keep local restore evidence and expose it in plan/receipt output.
- `irreversible_and_clearly_labeled`: the command stays plan-first and proof-first, but this CLI does not claim a direct restore path for that family.
- Snapshot-backed examples: `post patch`, `page patch`, `post bodylex ...`, `post bodymob ...`, `member update`, `newsletter update`, `tag update`, `tier update`, `offer update`.
- Some write families are currently dry-run-only because live apply requires explicit no-snapshot approval until this CLI can save the right before-state when possible.
- Dry-run-only examples: `webhook ...`, `theme ...`, `jobs run`, `image upload`, and create/copy or resource-create families.

Global flags must come before the subcommand:

```bash
ghost-api-tool --apply --yes post set-status ...
```

## Run history (local)

- `ghost-api-tool runs list [--limit N]`
- `ghost-api-tool runs show --run-id RUN_ID`

## Onboarding (first-time setup)

- `ghost-api-tool onboarding [--api-url https://your-site.ghost.io] [--accept-version v5.0] [--no-write-env]`

Notes:
- `--api-url` is the non-secret “API URL” value shown in Ghost Admin → Settings → Integrations → your custom integration.
- This command can create/update your local `.env` (no secrets are ever written by the tool).

## Auth

- `ghost-api-tool auth check [--full-site]`

## Content (read-only, public content)

These commands use the Ghost **Content API** and do not require `GHOST_ADMIN_API_URL` / `GHOST_ADMIN_API_KEY`.
They require `GHOST_CONTENT_API_URL` and `GHOST_CONTENT_API_KEY`.

- `ghost-api-tool content posts list [--limit N] [--page N] [--filter FILTER] [--fields FIELDS] [--include INCLUDE] [--order ORDER] [--formats FORMATS]`
- `ghost-api-tool content posts get (--id ID | --slug SLUG) [--fields FIELDS] [--include INCLUDE] [--formats FORMATS]`
- `ghost-api-tool content pages list [--limit N] [--page N] [--filter FILTER] [--fields FIELDS] [--include INCLUDE] [--order ORDER] [--formats FORMATS]`
- `ghost-api-tool content pages get (--id ID | --slug SLUG) [--fields FIELDS] [--include INCLUDE] [--formats FORMATS]`
- `ghost-api-tool content tags list [--limit N] [--page N] [--filter FILTER] [--fields FIELDS] [--include INCLUDE] [--order ORDER]`
- `ghost-api-tool content tags get (--id ID | --slug SLUG) [--fields FIELDS] [--include INCLUDE]`
- `ghost-api-tool content authors list [--limit N] [--page N] [--filter FILTER] [--fields FIELDS] [--include INCLUDE] [--order ORDER]`
- `ghost-api-tool content authors get (--id ID | --slug SLUG) [--fields FIELDS] [--include INCLUDE]`
- `ghost-api-tool content tiers list [--include INCLUDE] [--limit N] [--page N]`
- `ghost-api-tool content settings get`

Notes:
- `--page` is optional; if omitted, the tool fetches all pages and returns a `fetched` summary.
- `--formats` is supported on posts/pages (example: `html,plaintext`).

## Newsletter

- `ghost-api-tool newsletter list [--limit N] [--page N] [--fields FIELDS]`
- `ghost-api-tool newsletter get --id ID`
- `ghost-api-tool newsletter create --name NAME [--description TEXT] [--sender-reply-to newsletter|support] [--subscribe-on-signup true|false] [--opt-in-existing]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool newsletter update --id ID [--name NAME] [--description TEXT] [--sender-name NAME] [--sender-email EMAIL] [--sender-reply-to newsletter|support] [--subscribe-on-signup true|false] [--show-feature-image true|false] [--show-badge true|false]` (requires `--apply --yes`; recovery: `snapshot_plus_restore`)

Notes:
- Updating `sender_email` requires clicking a verification email from Ghost before it takes effect.

## Member

- `ghost-api-tool member list [--filter FILTER] [--limit N] [--page N] [--order ORDER] [--fields FIELDS] [--include labels,newsletters] [--include-emails] [--raw]`
- `ghost-api-tool member count [--filter FILTER]`
- `ghost-api-tool member get --id ID [--include labels,newsletters] [--include-emails] [--raw]`
- `ghost-api-tool member create --email EMAIL [--name NAME] [--note NOTE] [--label LABEL]... [--newsletter SLUG_OR_ID]...` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool member update --id ID [--set-name NAME] [--set-note NOTE] [--add-label LABEL]... [--remove-label LABEL]... [--replace-labels "A|B|C"] [--subscribe-newsletter SLUG_OR_ID]... [--unsubscribe-newsletter SLUG_OR_ID]...` (requires `--apply --yes`; recovery: `snapshot_plus_restore`)
- `ghost-api-tool member import --csv members.csv [--default-label LABEL]... [--default-newsletter SLUG_OR_ID]... [--mode create-only|upsert] [--sleep-ms N] [--continue-on-error]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool member export-engagement --out OUT.csv [--filter FILTER] [--include-emails] [--limit N] [--max-pages N]`

Safety:
- Emails are redacted in command output by default; use `--include-emails` only when you explicitly need it.
- `--raw` prints the full API payload and may include sensitive member fields.
Notes:
- For convenience, `--filter all` is treated as “no filter” (list/count everything).

## Post

- `ghost-api-tool post get (--slug SLUG | --id ID) [--formats html,lexical]`
- `ghost-api-tool post id (--slug SLUG | --id ID)`
- `ghost-api-tool post find [--filter FILTER] [--limit N] [--page N] [--order "published_at desc"] [--formats html,lexical]`
- `ghost-api-tool post copy (--slug SLUG | --id ID)` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool post authors audit [--out-dir DIR] [--filter FILTER] [--primary-author-name NAME] [--ghost-admin-name NAME] [--limit N] [--max-pages N] [--force]`
- `ghost-api-tool post email-stats-export --out OUT.csv [--filter FILTER] [--limit N] [--max-pages N] [--include-unsent]`
- `ghost-api-tool post images export-ledger --out OUT.csv [--filter FILTER] [--limit N] [--max-pages N] [--include tags] [--order "published_at desc"]`
- `ghost-api-tool post links audit [--filter FILTER] [--out-dir DIR] [--include-pages] [--internal-host HOST]...`
- `ghost-api-tool post links tag-candidates --tag TAG... [--out-dir DIR] [--filter FILTER] [--status published|draft|scheduled|any] [--hub-limit N] [--hub-metric lexical_word_count|none]`
- `ghost-api-tool post links amazon-audit [--out-dir DIR] [--filter FILTER] [--status published|draft|scheduled|any] [--require-affiliate-tag]`
- `ghost-api-tool post audit (--slug SLUG | --id ID) [--legacy-host HOST]... [--enforce-caption-policy]`
- `ghost-api-tool post create --title TITLE [--slug SLUG] [--status draft|published] [--visibility public|members|paid] (--html-file PATH | --lexical-file PATH) [--source html]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool post delete (--slug SLUG | --id ID) [--require-current draft|published]` (requires `--apply --yes`; recovery: `snapshot_plus_restore`)
- `ghost-api-tool post set-status (--slug SLUG | --id ID) --to draft|published|scheduled [--require-current draft] [--published-at ISO] [--newsletter SLUG] [--email-segment FILTER] [--email-only]` (when applying, requires `--apply --yes`; recovery: `snapshot_plus_restore` unless the apply can trigger email delivery, which stays `irreversible_and_clearly_labeled`)
- `ghost-api-tool post patch (--slug SLUG | --id ID) --file patch.json [--require-current draft] [--source html]` (recovery: `snapshot_plus_restore`)
- `ghost-api-tool post convert-from-html (--slug SLUG | --id ID) [--require-current draft] [--from-mobiledoc] [--allow-published]` (when converting mobiledoc, apply requires `--apply --yes`; recovery: `snapshot_plus_restore`)
- `ghost-api-tool post set-feature-image (--slug SLUG | --id ID) --file PATH [--upload-name NAME] [--alt TEXT] [--caption TEXT]` (recovery: `snapshot_plus_restore`)
- `ghost-api-tool post set-feature-from-body (--slug SLUG | --id ID) [--nth N] [--alt TEXT] [--caption TEXT] [--require-current draft] [--allow-published]` (recovery: `snapshot_plus_restore`)
- `ghost-api-tool post freepik apply-one (--slug SLUG | --id ID) --featured-alt TEXT --featured-caption TEXT [--freepik-featured-id ID] [--featured-file PATH] [--freepik-inventory-csv PATH] [--freepik-downloads-root DIR] [--featured-upload-name NAME] [--placements-file placements.json | --body-images-json body_images.json] [--publish] [--diff] [--no-fix-split-numbered-lists] [--no-fix-numbered-paragraphs] [--snapshots-dir DIR] [--tracking-csv PATH]` (manual alt/caption; recovery: `snapshot_plus_restore`, but `--publish` applies stay `irreversible_and_clearly_labeled`)
- `ghost-api-tool post scaffold seo-patch (--slug SLUG | --id ID) --out PATH [--force] [--include-internal-tags]`

### Export an image ledger (featured + body)

Writes a CSV with one row per image across posts:
- `image_kind=featured` for `feature_image`
- `image_kind=body` for images extracted from the Lexical document

Example:

```bash
ghost-api-tool post images export-ledger --out <PROJECT_DIR>/snapshots/ghost_images_ledger.csv
```

`post freepik apply-one` notes:
- `--featured-alt` / `--featured-caption` are required and must be authored manually.
- `--featured-caption` (and any body image `caption`) must end with `(stock image; for illustration only).`
- By default, it also normalizes `Instructions` when steps are stored as numbered paragraphs (`<p>1. ...</p>`), converting them to a proper ordered list; disable with `--no-fix-numbered-paragraphs`.
- `--placements-file` is the same JSON format used by `post bodylex image sync-before-headings` (expects `src` URLs).
- `--body-images-json` is for local files; the command uploads them to Ghost and inserts them before headings.
- When using `--body-images-json`, dry-run refuses if any `file` path does not exist (to avoid partial applies).

`body_images.json` format for `post freepik apply-one --body-images-json`:

```json
[
  {
    "freepik_id": "123456",
    "file": "<DOWNLOADS_ROOT>/by-post/my-post/123456--example.jpg",
    "upload_name": "my-post-body-1.jpg",
    "heading": "Instructions",
    "heading_occurrence": 1,
    "alt": "Manual alt text",
    "caption": "Manual caption (stock image; for illustration only)."
  }
]
```

## Post body (Lexical mode)

- `ghost-api-tool post bodylex inspect (--slug SLUG | --id ID)`
- `ghost-api-tool post bodylex scaffold captions-map (--slug SLUG | --id ID) --out PATH [--force] [--mode missing|all|nonconforming] [--include-context] [--all]`
- `ghost-api-tool post bodylex image replace-src (--slug SLUG | --id ID) --old-src URL --new-src URL [--alt TEXT] [--caption TEXT] [--title TEXT] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image replace-many (--slug SLUG | --id ID) --map mapping.json [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image replace-after-heading (--slug SLUG | --id ID) --heading TEXT --new-src URL [--expect-old-src URL] [--nth-after-heading N] [--heading-occurrence N] [--alt TEXT] [--caption TEXT] [--title TEXT] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image set-meta (--slug SLUG | --id ID) --src URL [--alt TEXT] [--caption TEXT] [--title TEXT] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image insert-after-heading (--slug SLUG | --id ID) --heading TEXT --src URL --template-src URL [--heading-occurrence N] [--alt TEXT] [--caption TEXT] [--title TEXT] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image move-before-heading (--slug SLUG | --id ID) --src URL --heading TEXT [--heading-occurrence N] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image sync-before-headings (--slug SLUG | --id ID) --placements-file placements.json [--no-fix-split-numbered-lists] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex image delete-by-src (--slug SLUG | --id ID) --src URL [--all] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex fix-numbered-list-after-heading (--slug SLUG | --id ID) --heading TEXT [--heading-occurrence N] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex fix-numbered-paragraphs-after-heading (--slug SLUG | --id ID) --heading TEXT [--heading-occurrence N] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex fix-bullet-lists-split-html-cards (--slug SLUG | --id ID) [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex convert-html-list-cards (--slug SLUG | --id ID) [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex fix-link-whitespace (--slug SLUG | --id ID) [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex linkify (--slug SLUG | --id ID) --paragraph-contains TEXT [--paragraph-occurrence N] --anchor-text TEXT [--anchor-occurrence N] --url URL [--include-list-items] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex insert-link-paragraph-after-heading-section-end (--slug SLUG | --id ID) --heading TEXT [--heading-occurrence N] --link-text TEXT --url URL [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex clear-heading-bold (--slug SLUG | --id ID) [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex set-amazon-link-rel (--slug SLUG | --id ID) [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex set-paid-link-rel (--slug SLUG | --id ID) (--host HOST | --all-external) [--internal-host HOST] [--rel "TOKENS..."] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex unlink-by-url (--slug SLUG | --id ID) --url URL [--url URL]... [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex unlink-by-url-after-heading (--slug SLUG | --id ID) --after-heading "Conclusion" --url URL [--url URL]... [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex delete-link-items-by-url-after-heading (--slug SLUG | --id ID) --after-heading "Conclusion" --url URL [--url URL]... [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex unlink-internal-caption-links (--slug SLUG | --id ID) [--internal-host HOST] [--diff] [--require-current draft] [--allow-published]`
- `ghost-api-tool post bodylex insert-links-section (--slug SLUG | --id ID) --section-heading TEXT --intro TEXT --link "ANCHOR|URL" [--link "ANCHOR|URL"]... [--before-heading "Conclusion"] [--skip-url URL] [--diff] [--require-current draft] [--allow-published]`

By default, applying a `post bodylex ...` edit is refused unless the post is `draft`. Use `--allow-published` to override (e.g. for published/scheduled posts).

`mapping.json` format for `replace-many`:

```json
{
  "https://old.example/image.jpg": {
    "new_src": "https://new.example/image.jpg",
    "alt": "Optional alt",
    "caption": "Optional caption",
    "title": "Optional title"
  },
  "https://old.example/another.jpg": "https://new.example/another.jpg"
}
```

## Post body (Mobiledoc mode)

Some imported posts use `mobiledoc` instead of `lexical`.

- `ghost-api-tool post bodymob inspect (--slug SLUG | --id ID)`
- `ghost-api-tool post bodymob scaffold captions-map (--slug SLUG | --id ID) --out PATH [--force] [--mode missing|all|nonconforming] [--include-context] [--all]`
- `ghost-api-tool post bodymob image replace-many (--slug SLUG | --id ID) --map mapping.json [--diff] [--require-current draft] [--allow-published]`

## Page

- `ghost-api-tool page get (--slug SLUG | --id ID) [--formats html,lexical]`
- `ghost-api-tool page find [--filter FILTER] [--limit N] [--page N] [--order "published_at desc"] [--formats html,lexical]`
- `ghost-api-tool page create --title TITLE [--slug SLUG] [--status draft|published] [--visibility public|members|paid] (--html-file PATH | --lexical-file PATH) [--source html]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool page copy (--slug SLUG | --id ID)` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool page delete (--slug SLUG | --id ID) [--require-current draft|published]` (requires `--apply --yes`; recovery: `snapshot_plus_restore`)
- `ghost-api-tool page set-status (--slug SLUG | --id ID) --to draft|published|scheduled [--require-current draft] [--published-at ISO]` (when applying, requires `--apply --yes`; recovery: `snapshot_plus_restore`)
- `ghost-api-tool page patch (--slug SLUG | --id ID) --file patch.json [--require-current draft] [--source html]` (recovery: `snapshot_plus_restore`)
- `ghost-api-tool page set-feature-image (--slug SLUG | --id ID) --file PATH [--upload-name NAME] [--alt TEXT] [--caption TEXT]` (recovery: `snapshot_plus_restore`)
- `ghost-api-tool page sync-md --slug SLUG --title TITLE --md-file PATH [--status draft|published] [--visibility public|members|paid] [--replace-existing]` (when replacing an existing page, use `--yes`; brand-new create applies stay requires explicit no-snapshot approval when no saved snapshot is available; recovery: `snapshot_plus_restore`)

## Post body (HTML card mode)

- `ghost-api-tool post body show-images (--slug SLUG | --id ID)`
- `ghost-api-tool post body set-captions (--slug SLUG | --id ID) --captions-file map.json [--diff]`

`map.json` format:

```json
{
  "https://example.com/image.jpg": "Caption text"
}
```

## Image

- `ghost-api-tool image upload --file PATH [--upload-name NAME] [--purpose image|profile_image|icon] [--ref TEXT]` (requires explicit no-snapshot approval when no saved snapshot is available)

## Tag

- `ghost-api-tool tag list [--visibility all|public|internal] [--include-count] [--order "name asc"] [--limit N] [--page N]`
- `ghost-api-tool tag audit [--exclude-empty]`
- `ghost-api-tool tag create --name NAME [--slug SLUG] [--description TEXT] [--visibility public|internal] [--meta-title TEXT] [--meta-description TEXT] [--feature-image URL]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool tag update --id TAG_ID [--name NAME] [--slug SLUG] [--description TEXT] [--visibility public|internal] [--meta-title TEXT] [--meta-description TEXT] [--feature-image URL]` (requires `--apply`)
- `ghost-api-tool tag delete --id TAG_ID` (requires `--apply --yes`)
- `ghost-api-tool tag delete-zero [--visibility all|public|internal] [--limit N]` (bulk; requires `--apply --yes`)
- `ghost-api-tool tag merge --from-slug FROM --to-slug TO [--delete-from-tag] [--limit N]` (bulk; requires `--apply --yes`)

## Tier

- `ghost-api-tool tier list [--limit N] [--page N] [--order ORDER] [--filter FILTER] [--fields FIELDS] [--include monthly_price,yearly_price,benefits]`
- `ghost-api-tool tier get --id ID [--include INCLUDE]`
- `ghost-api-tool tier create --name NAME [--description TEXT] [--welcome-page-url URL] [--visibility public|none] [--monthly-price N] [--yearly-price N] [--currency CODE] [--benefit TEXT]...` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool tier update --id ID [--name NAME] [--description TEXT] [--welcome-page-url URL] [--visibility public|none] [--active true|false] [--monthly-price N] [--yearly-price N] [--currency CODE] [--benefit TEXT]...` (requires `--apply`)

## Offer

- `ghost-api-tool offer list [--limit N] [--page N] [--order ORDER] [--filter FILTER] [--fields FIELDS]`
- `ghost-api-tool offer get --id ID`
- `ghost-api-tool offer create --name NAME --code CODE --type percent|fixed --cadence month|year --duration once|forever|repeating --amount N --tier-id ID [--display-title TEXT] [--display-description TEXT] [--duration-in-months N] [--currency CODE] [--currency-restriction true|false]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool offer update --id ID [--name NAME] [--code CODE] [--display-title TEXT] [--display-description TEXT]` (requires `--apply`)

## Theme

- `ghost-api-tool theme upload --file PATH [--upload-name NAME]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool theme activate --name THEME_NAME` (requires explicit no-snapshot approval when no saved snapshot is available)

## Webhook

- `ghost-api-tool webhook create --event EVENT --target-url URL [--name NAME] [--api-version VERSION] [--secret-file PATH]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool webhook update --id ID [--event EVENT] [--target-url URL] [--name NAME] [--api-version VERSION]` (requires explicit no-snapshot approval when no saved snapshot is available)
- `ghost-api-tool webhook delete --id ID` (requires explicit no-snapshot approval when no saved snapshot is available)

## Jobs

- `ghost-api-tool jobs run --file jobs.csv [--limit N]` (dry-run only until mixed row writes can save before-state when possible)

`jobs.csv` must have a header row and an `action` column. Supported actions:
- File paths (e.g. `file`, `map`, `captions_file`) are resolved relative to the current working directory (prefer running from the repo root or use absolute paths).
- `post.patch` (requires `file`)
- `post.set-status` (requires `to`)
- `post.body.set-captions` (requires `captions_file`)
- `post.bodylex.image.replace-many` (requires `map`; optional: `allow_published=1`, `diff=1`)
- `post.bodymob.image.replace-many` (requires `map`; optional: `allow_published=1`, `diff=1`)
