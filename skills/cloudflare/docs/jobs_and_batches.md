# Jobs and batches

This tool includes a `jobs` command for safe batch operations (CSV).

Design goals:
- Dry-run by default (plan first).
- Explicit apply gates for writes and sensitive outputs.
- Stop on first error (no partial “keep going” mode).
- One JSON summary object to stdout.

## Run a batch

Dry-run plan:
- `cloudflare-api-tool jobs run --file jobs.csv`

Apply:
- Reads can run with `--apply` (still safe; they don’t write to Cloudflare).
- If any step is a write, live apply needs saved before-state for each changed resource or explicit no-snapshot approval; unsupported, ambiguous, or failed safety-check rows still stop.
- If any read-like step returns sensitive data, it still requires a file output.

## CSV format

Recommended headers:
- `operation_id` (preferred when present)
- or `method` + `path` (when `operation_id` is missing)
- `path_params_json` (JSON object string; required when the path has `{...}` params)
- `query_json` (JSON object string; optional)
- `body_json_file` / `body_bytes_file` / `multipart_spec_file` (mutually exclusive; optional)
- `content_type` (optional)
- `out` + `overwrite` (required for sensitive outputs; file path must be under `--project-dir`)

Tip:
- Use `cloudflare-api-tool operations list` to find `operation_id` values from the local snapshot extracts.
