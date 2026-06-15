# Safety model

Open Library is safest when you treat the agent as a focused reader for public books, authors, editions, subjects, and ISBN data. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Look up one book, author, or ISBN first, then summarize only from the returned record."

## Core safety rules

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
