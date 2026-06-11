# SEO capability probe (simple)

This folder contains a small, read-only “capability probe” that helps us answer:

- Which SEO plugin is likely installed?
- If SEOPress is installed, do we have API access to its write endpoints as the current user?

The goal is to quickly classify a site for our VA workflow:

- **Green**: SEO fields can be set via API (typically **SEOPress**).
- **Yellow**: maybe possible (plugin/version/settings/permissions dependent).
- **Red**: not possible without extra enablement (typical for Yoast/Rank Math).

## What it does (safe)

- Auth check: `GET /wp-json/wp/v2/users/me`
- Picks a target post (or uses your `--id/--slug`)
- Detects plugin “signals” from the post response (read-only head JSON fields)
- Reads the REST API index (`GET /wp-json`) to see which namespaces/routes exist and which HTTP methods they declare (this is the most reliable “is it installed / does it support PUT” signal without doing a write)

By default it does **not** modify any post.

## How to run

From the tool folder (needs `PYTHONPATH=src`):

```bash
PYTHONPATH=src python3 docs/seo_plugins/capability_probe.py --env-file .env
```

Target a specific post:

```bash
PYTHONPATH=src python3 docs/seo_plugins/capability_probe.py --env-file .env --post-type posts --slug my-post-slug
PYTHONPATH=src python3 docs/seo_plugins/capability_probe.py --env-file .env --post-type pages --id 123
```

## Output

The script prints JSON to stdout with:

- `auth.me`: current user (from `/users/me`)
- `target`: which post it used for probing
- `signals`: detected fields like `yoast_head_json`, `aioseo_head_json`
- `plugins.seopress`: endpoint availability + allowed methods (`PUT` is what we need for writes)
- `recommendation`: a simple summary

## Interpreting results (quick)

- If `plugins.seopress.can_write=true`: we can implement “set SEO title/desc/robots/social” via SEOPress REST endpoints.
- If Yoast/Rank Math signals are present but `plugins.seopress.detected=false`: assume SEO fields are **not writable** via API without additional enablement.
