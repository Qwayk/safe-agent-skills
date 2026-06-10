# Safety model

This tool is intentionally read-only.

- No auth commands.
- No write, no raw request, no batch apply workflow.
- No destructive actions.
- Every run uses a single, validated endpoint and emits one JSON result.

Use it as a review-first helper:

- Query only what you need.
- Use `--limit` and `--offset` for list calls.
- Keep volume low to stay within public endpoint behavior.

`subjects` is experimental. Test carefully before relying on it in scripts.
