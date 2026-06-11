# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no keys).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Common PA-API errors

- `InvalidSignatureException`: usually wrong region/host, wrong secret key, or a system clock issue.
- `TooManyRequests`: you are throttled; retry later (jobs already retries a little).
