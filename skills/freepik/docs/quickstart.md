# Quickstart

If you're non-technical, start with [What you can do](use_cases.md) and [Connect your account](onboarding.md).

This page is technical. It shows the exact Freepik CLI commands.

## 1) Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2) Configure

Create `.env` from `.env.example` and fill:

- `FREEPIK_API_BASE_URL`
- `FREEPIK_BASE_URL` (legacy alias)
- `FREEPIK_API_KEY`

Freepik auth defaults to:

- `FREEPIK_AUTH_HEADER=x-freepik-api-key`
- `FREEPIK_AUTH_PREFIX=` (empty)

Only change those auth settings if Freepik support tells you to.

Optional: if you want stable defaults for downloads and the inventory CSV, create a small non-secret config JSON and pass `--config`.

Useful keys:

- `downloads_dir`
- `inventory_csv`

## 3) Check auth

```bash
freepik-api-tool auth check
```

## 4) Run safe reads first

Search:

```bash
freepik-api-tool search photos --query "roasted turkey" --limit 10 --shortlist
```

Get details for a chosen candidate:

```bash
freepik-api-tool resource get --id RESOURCE_ID
```

Preview a chosen asset:

```bash
freepik-api-tool preview --id RESOURCE_ID
freepik-api-tool preview --id RESOURCE_ID --save-preview previews/
```

`--save-preview` writes local preview files only. Delete them manually when you no longer need them.

## 5) Build a dry-run download plan

```bash
freepik-api-tool download --id RESOURCE_ID --format jpg --out-dir downloads --inventory licensed-downloads-ledger.csv
```

Safety:

- `download` refuses unless the resource detail clearly shows `is_ai_generated=false` and `has_prompt=false`.
- Dry-run does not call the licensed download endpoint or write files.

## 6) Apply only after review

Licensed live download needs explicit no-snapshot approval:

```bash
freepik-api-tool --apply --ack-no-snapshot download --id RESOURCE_ID --format jpg --out-dir downloads --inventory licensed-downloads-ledger.csv
```

Approved apply writes the file and an inventory row, then returns verification details in the JSON output.

Without `--ack-no-snapshot`, the tool refuses before the licensed download endpoint, local file write, or inventory row write.

Optional resize for photos:

```bash
freepik-api-tool --apply --ack-no-snapshot download --id RESOURCE_ID --format jpg --image-size 1000px --out-dir downloads --inventory licensed-downloads-ledger.csv
```

## 7) Batch apply only after review

Generate a local jobs CSV first:

```bash
freepik-api-tool search photos --query "roasted turkey" --limit 10 --write-jobs jobs.csv --job-format jpg --job-image-size 2000px
```

Then apply the batch only after you review the file:

```bash
freepik-api-tool --apply --yes --ack-no-snapshot jobs run --file jobs.csv --out-dir downloads --inventory licensed-downloads-ledger.csv
```

## Useful filtering notes

Freepik's `/resources` endpoint uses `filters` in `deepObject` style. Some filters are arrays, so `content_type` must use `[]`:

```bash
freepik-api-tool search images \
  --query "roasted turkey" \
  --limit 10 \
  --param 'filters[content_type][]=photo'
```

Best-effort AI exclusion:

```bash
freepik-api-tool search images \
  --query "roasted turkey" \
  --limit 10 \
  --param 'filters[content_type][]=photo' \
  --exclude-ai
```

`--exclude-ai` fetches resource detail for each result. It helps, but you should still verify the previews by eye.

## Advanced response parsing overrides

If the API returns license or download URLs in an unexpected place, use:

- `--license-url-jsonpath`
- `--download-url-jsonpath`

Or set defaults in `.env`:

- `FREEPIK_LICENSE_URL_JSONPATH`
- `FREEPIK_DOWNLOAD_URL_JSONPATH`

## Pricing note

Freepik API pricing can change over time. Check Freepik's current pricing and keep batch sizes reasonable.
