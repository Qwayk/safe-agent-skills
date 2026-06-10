# Safety model

This tool is read-only by design.

- Only shipped `GET` commands are enabled.
- No write, plan, apply, or receipt flow exists.
- Unsupported parser/input forms return standard validation errors.
- Requests for rows marked excluded in `docs/api_coverage.md` should be reported as `excluded by choice: read-only tool`.
- Output is always one JSON object per command.
- Secrets (for example `PIPEDRIVE_API_TOKEN`) are never printed.

## File download safety

- `files download` runs with metadata-only behavior.
- It makes a `HEAD` request to get size and type.
- It does not follow redirects by default.
- It does not download binary body content.
