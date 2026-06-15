# Safety model

Pipedrive is safest when you treat the agent as a focused reader for CRM deals, leads, activities, people, organizations, products, and pipelines. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Read the pipeline, deal, or lead first, then keep the work to reporting because this public tool is read-only."

## Core safety rules

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
