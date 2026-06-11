# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Live gate

If a command is refusing to call the API, make sure you added `--live`.

If a command is refusing to apply, check whether it requires:
- `--apply`
- `--yes`
- `--ack-irreversible` (DELETE-like)
- `--ack-spend-money` (payment/billing)
- `--plan-in` (high-risk applies)
