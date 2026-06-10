# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

First-time setup helper (recommended):

```bash
ghost-api-tool onboarding
```

## Install (minimal)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (contributors): install dev extras:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## Configure

Copy `.env.example` to `.env` and fill in:
- `GHOST_ADMIN_API_URL`
- `GHOST_ADMIN_API_KEY`
- `GHOST_ACCEPT_VERSION`

Never commit `.env`.

Tip (v2 tool artifacts): run from the tool folder (or pass `--env-file .env`) so the tool-managed folders `.state/` and `backup-snapshots/` land next to your env file and are gitignored.

Important: project outputs (exported reports/CSVs, one-off patch JSON files, screenshots, etc.) should live under your project folder (example: `<PROJECT_DIR>/...`), not inside the tool folder.

Tip: if you keep project files outside the tool repo, pass `--project-dir <PROJECT_DIR>` so commands that create local outputs (or read local helper files) can resolve paths consistently.

## Smoke test

```bash
ghost-api-tool auth check
```

If you need more debug info from `/site/`, run:

```bash
ghost-api-tool auth check --full-site
```

## Useful read-only audits

Internal links + orphans (export reports):

```bash
ghost-api-tool post links audit --include-pages --out-dir <PROJECT_DIR>/internal-linking/reports
```

Amazon links (amzn.to + amazon.*):

```bash
ghost-api-tool post links amazon-audit --status any --out-dir <PROJECT_DIR>/internal-linking/reports
```

## Members + newsletters (email marketing)

List newsletters:

```bash
ghost-api-tool newsletter list
```

List members (safe output; emails are redacted by default):

```bash
ghost-api-tool member list --limit 20
```

Tag a member with a label (dry-run first):

```bash
ghost-api-tool member update --id MEMBER_ID --add-label warmup10
ghost-api-tool --apply --yes member update --id MEMBER_ID --add-label warmup10
```

Export engagement fields to CSV:

```bash
ghost-api-tool member export-engagement --out <PROJECT_DIR>/snapshots/ghost_members_engagement.csv
```

Export email delivery stats for sent posts:

```bash
ghost-api-tool post email-stats-export --out <PROJECT_DIR>/snapshots/ghost_email_stats.csv
```

## Publish a page from Markdown (legal pages)

If you have a Markdown file and want Ghost to convert it to the modern editor format (Lexical), use `page sync-md`.

Dry-run (shows what would happen):

```bash
ghost-api-tool page sync-md --slug privacy-policy --title "Privacy Policy" --md-file <PROJECT_DIR>/legal/privacy-policy.md --status published --replace-existing
```

Apply:

```bash
ghost-api-tool --apply --yes page sync-md --slug privacy-policy --title "Privacy Policy" --md-file <PROJECT_DIR>/legal/privacy-policy.md --status published --replace-existing
```

## Recovery evidence

- Snapshot-backed families write JSON snapshots under `backup-snapshots/` next to your `--env-file` (grouped by domain and date). Their plans and receipts show `recovery.end_state = snapshot_plus_restore`.
- Some write families need extra care because this CLI cannot always save before-state for them. Important examples are `webhook ...`, `theme ...`, `jobs run`, `image upload`, and create/copy or resource-create flows. Use the plan, require explicit no-snapshot approval where apply is supported, and stop only for a real blocker such as no safe executor or no verification path.
- Webhook applies save proof in `.state/webhooks/index.jsonl` instead of claiming a restorable snapshot.

## First safe body edit (Lexical)

1) Inspect images in a normal Ghost post:

```bash
ghost-api-tool post bodylex inspect --slug YOUR-POST-SLUG
```

If `post audit` reports it can’t parse Lexical, the post might be in `mobiledoc` (older import).
Check with:

```bash
ghost-api-tool post bodymob inspect --slug YOUR-POST-SLUG
```

Use `post bodymob ...` commands for those posts.

2) Dry-run an inline image replacement (prints a diff, no writes):

```bash
ghost-api-tool post bodylex image replace-src --slug YOUR-POST-SLUG --old-src OLD_URL --new-src NEW_URL --diff
```

3) Apply (recommended: gate on draft):

```bash
ghost-api-tool --apply post bodylex image replace-src --slug YOUR-POST-SLUG --old-src OLD_URL --new-src NEW_URL --require-current draft
```

## Speed helpers (manual workflow)

Scaffold a mapping file for captions/alts (so you can fill them manually, then apply once):

```bash
ghost-api-tool post bodylex scaffold captions-map --slug YOUR-POST-SLUG --mode all --include-context --out captions-map.json
ghost-api-tool post bodylex image replace-many --slug YOUR-POST-SLUG --map captions-map.json --diff
ghost-api-tool --apply post bodylex image replace-many --slug YOUR-POST-SLUG --map captions-map.json --require-current draft
```

If you only want to fill missing captions (faster, but can leave inconsistent captions), omit `--mode all`:

```bash
ghost-api-tool post bodylex scaffold captions-map --slug YOUR-POST-SLUG --out captions-map.json
```

Scaffold an editable patch file for title/excerpt/meta/social/tags:

```bash
ghost-api-tool post scaffold seo-patch --slug YOUR-POST-SLUG --out seo.patch.json
ghost-api-tool post patch --slug YOUR-POST-SLUG --file seo.patch.json --require-current draft
ghost-api-tool --apply post patch --slug YOUR-POST-SLUG --file seo.patch.json --require-current draft
```

Set a feature image from the Nth body image (no upload):

```bash
ghost-api-tool post set-feature-from-body --slug YOUR-POST-SLUG --nth 1
ghost-api-tool --apply post set-feature-from-body --slug YOUR-POST-SLUG --nth 1 --require-current draft --alt "..." --caption "..."
```

## Tags (inventory + safe cleanup)

List tags with post counts:

```bash
ghost-api-tool tag list --visibility all --include-count --order "count.posts desc"
```

Audit tags for cleanup candidates (duplicates + 0-post tags):

```bash
ghost-api-tool tag audit
```

Delete all tags with `count.posts=0` (bulk; safe cleanup). Dry-run:

```bash
ghost-api-tool tag delete-zero
```

Apply (requires both confirmations):

```bash
ghost-api-tool --apply --yes tag delete-zero
```
