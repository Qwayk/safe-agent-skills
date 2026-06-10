# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

## Install/dev

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Configure

Create `.env` from `.env.example`:
- `FREEPIK_API_BASE_URL`
- `FREEPIK_BASE_URL` (legacy alias)
- `FREEPIK_API_KEY`

Auth defaults to the Freepik OpenAPI v1 scheme:
- `FREEPIK_AUTH_HEADER=x-freepik-api-key`
- `FREEPIK_AUTH_PREFIX=` (empty)

Only change these if Freepik support/documents a different auth method for your account.

Optional: if you want stable defaults for your downloads folder and inventory CSV, create a non-secret project config JSON and pass `--config`:
- `downloads_dir`: directory where files will be saved (default: `<PROJECT_DIR>/downloads`)
- `inventory_csv`: path to your inventory CSV (default: `<PROJECT_DIR>/licensed-downloads-ledger.csv`)

## Smoke test

```bash
freepik-api-tool auth check
```

## Search

```bash
freepik-api-tool search images --query "roasted turkey" --limit 10
```

Photo-first default:

```bash
freepik-api-tool search photos --query "roasted turkey" --limit 10
```

Optional language:

```bash
freepik-api-tool --accept-language en-US search images --query "roasted turkey" --limit 10
```

Pass extra query parameters (verbatim to the API):

```bash
freepik-api-tool search images --query "turkey" --param 'filters[license][freemium]=1' --param 'filters[orientation]=horizontal'
```

### Shortlist + jobs generation (read + local-only)

Shortlist (compact JSON for selection):

```bash
freepik-api-tool search photos --query "roasted turkey" --limit 10 --shortlist
```

Write a jobs CSV for later batch downloads (no API writes; local file output only):

```bash
freepik-api-tool search photos --query "roasted turkey" --limit 10 --write-jobs jobs.csv --job-format jpg --job-image-size 2000px
```
Delete the CSV file manually if you only needed it for one job run.

### Search: photos only + best-effort exclude AI

Freepik’s `/resources` endpoint uses `filters` in `deepObject` style. Some filters are **arrays**.
For example, `content_type` must be sent as an array, so use `[]` in the key:

```bash
freepik-api-tool search images \
  --query "roasted turkey" \
  --limit 10 \
  --param 'filters[content_type][]=photo'
```

To best-effort exclude AI-generated results, use `--exclude-ai`:

```bash
freepik-api-tool search images \
  --query "roasted turkey" \
  --limit 10 \
  --param 'filters[content_type][]=photo' \
  --exclude-ai
```

This works by fetching resource detail for each result and filtering when the detail indicates AI via flags like `is_ai_generated=true` or `has_prompt=true`. Not all resources expose these flags, so you must still validate by eye.

### Two practical workflows (how to use this tool)

When you (the human) ask “find me a good non‑AI photo for X”, there are two ways to work:

**Workflow A — fastest (shortlist-first, recommended default)**
1) Do one photos-only search: `filters[content_type][]=photo`.
2) Shortlist ~3–5 candidates by title + preview URL.
3) Inspect candidates **one-by-one**:
   - `resource get` (to check AI flags when available and to see related candidates)
   - `preview` (to quickly save/view the thumbnail)
4) Stop as soon as you have a winner (no need to check every result).

**Workflow B — strict (clean the whole list)**
1) Run `search ... --exclude-ai`.
2) This makes extra “detail” calls for each result and returns a cleaner list.

Why this exists:
- The search results list does not reliably include AI flags.
- Resource detail flags are best-effort, so you must still verify by eye.

### Recipe workflow (non‑AI + “discover similar”)

For recipes, the goal is usually **1 feature image + 1–2 extra angles** from the same photoshoot.

Start here:
- Tool workflow: `docs/recipe_workflow_recipes.md`
- Your project’s own protocol (if you have one) should live in your project folder (not inside this tool repo).

## Preview (no license / no inventory write)

```bash
freepik-api-tool preview --id RESOURCE_ID
freepik-api-tool preview --id RESOURCE_ID --save-preview <PREVIEWS_DIR>
```
`--save-preview` writes local preview files and must be cleaned up manually if needed.

## Download (dry-run, then apply)

Dry-run prints the plan with `no_snapshot_available` before_state metadata (no file download, no CSV write):

```bash
freepik-api-tool download --id RESOURCE_ID --format jpg --out-dir <DOWNLOADS_DIR> --inventory <INVENTORY_CSV>
```

Safety: `download` refuses unless the resource detail explicitly includes `is_ai_generated=false` AND `has_prompt=false` (missing/unknown flags are rejected).

Apply requires explicit no-snapshot approval when no saved snapshot exists:

```bash
freepik-api-tool --apply download --id RESOURCE_ID --format jpg --out-dir <DOWNLOADS_DIR> --inventory <INVENTORY_CSV>
```

Approved apply and batch receipts include a `recovery` block with `strategy=no_inverse`, `rollback_ready=false`, `automatic_rollback=false`, and `rollback_plan=null`, plus a refusal reason. Missing no-snapshot approval refuses before the licensed download endpoint, destination file, or inventory row.

Optional resize for photos (applies only to the `/download` endpoint):

```bash
freepik-api-tool --apply download --id RESOURCE_ID --format jpg --image-size 1000px --out-dir <DOWNLOADS_DIR> --inventory <INVENTORY_CSV>
```

apply requires explicit no-snapshot approval before reaching that `/download` endpoint.

If the API response contains URLs in unexpected locations, set JSONPaths:
- `--license-url-jsonpath` (applies to the **resource detail** JSON)
- `--download-url-jsonpath` (applies to the **download** JSON)

Or set defaults in `.env`:
- `FREEPIK_LICENSE_URL_JSONPATH`
- `FREEPIK_DOWNLOAD_URL_JSONPATH`

## Pricing note (Freepik API)

Freepik API pricing can change over time. Check the current pricing in Freepik’s official docs and keep batch sizes reasonable.
