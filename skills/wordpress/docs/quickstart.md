# Quickstart

If you want the human path first, start with [What you can do with WordPress](use_cases.md), [Connect your WordPress site](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the technical reference for install, setup, and first WordPress commands.

## Install

From the skill folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (dev tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## Configure

Create `.env` (or export env vars) using `.env.example`:
- `WP_BASE_URL`
- `WP_USERNAME`
- `WP_APP_PASSWORD` (Application Password; spaces are OK)

Notes:
- `WP_BASE_URL` should be the site root (example: `https://example.com`). If you paste a full API URL like `https://example.com/wp-json/wp/v2`, the tool will normalize it.
- Application Passwords require WordPress 5.6+ and may be disabled by some security plugins.

## First commands

```bash
wordpress-api-tool --version
wordpress-api-tool auth check
wordpress-api-tool discover post-types
wordpress-api-tool discover statuses
wordpress-api-tool discover taxonomies
wordpress-api-tool comments list --limit 3
wordpress-api-tool search query --query "hello" --limit 3
wordpress-api-tool terms list --taxonomy categories --query "news" --limit 5
wordpress-api-tool media find --query "banner" --limit 5
wordpress-api-tool post find --query "test" --limit 5
wordpress-api-tool post get --slug hello-world
wordpress-api-tool post truth --slug hello-world --resolve-urls
wordpress-api-tool post images --slug hello-world --include-featured
```

Optional (permission-restricted on many sites):

```bash
wordpress-api-tool users list --limit 5
wordpress-api-tool settings get
```

## Migration tracking (from WordPress export XML)

If you have WordPress export XML files, you can generate a `tracking.csv`:

```bash
wordpress-api-tool migration tracking-from-xml --xml export.xml --out <PROJECT_DIR>/tracking.csv
```

## First safe edit (dry-run, then apply)

Media Library caption (attachment metadata):

```bash
wordpress-api-tool media set --id 123 --caption "Photo: Stock site / License XYZ"
wordpress-api-tool --apply media set --id 123 --caption "Photo: Stock site / License XYZ"
```

Post-body captions (only Gutenberg `wp:image` blocks):

```bash
wordpress-api-tool post set-image-captions --slug hello-world --caption "Photo: Stock site / License XYZ"
wordpress-api-tool --apply post set-image-captions --slug hello-world --caption "Photo: Stock site / License XYZ"
```

Categories/tags (taxonomy terms) are also dry-run by default:

```bash
wordpress-api-tool post set-terms --slug hello-world --set --category-slug news --tag-slug featured
wordpress-api-tool --apply post set-terms --slug hello-world --set --category-slug news --tag-slug featured
```

Publishing (status change) is also dry-run by default:

```bash
wordpress-api-tool post set-status --slug hello-world --to publish --require-current draft
wordpress-api-tool --apply post set-status --slug hello-world --to publish --require-current draft
```

Same safe flow works for pages with `--post-type pages`:

```bash
wordpress-api-tool post set-status --post-type pages --slug about-us --to publish --require-current draft
wordpress-api-tool --apply post set-status --post-type pages --slug about-us --to publish --require-current draft
```

## Faster updates for many images

If you have a lot of images with different captions, put them in a JSON file and run a single command:

```bash
wordpress-api-tool media set-batch --file updates.json
wordpress-api-tool --apply media set-batch --file updates.json
wordpress-api-tool post set-image-captions --slug hello-world --captions-file updates.json
wordpress-api-tool --apply post set-image-captions --slug hello-world --captions-file updates.json
```

## Bulk media download (plan, then apply)

You can download many Media Library files to your computer from a CSV/JSON list.

Dry-run (compute filenames/paths, no local writes):

```bash
wordpress-api-tool media download-batch --file items.json --plan-out plan.media_download_batch.json
```

Apply (writes files locally; requires `--apply --yes`):

```bash
wordpress-api-tool --apply --yes media download-batch --file items.json --receipt-out receipt.media_download_batch.json
```
