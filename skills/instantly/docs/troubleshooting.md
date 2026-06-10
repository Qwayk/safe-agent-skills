# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## 401 Unauthorized / invalid API key

- Run `instantly-api-tool --output json auth check`.
- Confirm your `.env` contains `INSTANTLY_API_KEY=...`.
- Confirm the key scopes in Instantly match the actions you’re trying to run.

## Rate limits / 429

- Reduce pagination sizes (`--limit`) and avoid tight loops.
- If you need to run a lot of reads, add a small sleep between calls in your wrapper agent logic.
- Instantly docs (linked in `docs/references.md`) document workspace-wide limits of **100 requests / 10 seconds** and **600 requests / minute**, and the emails list endpoint is additionally limited to **20 requests / minute**.
- This tool defaults `emails list` to `--limit 20` to encourage safe reads (you can override it if you know what you’re doing).
