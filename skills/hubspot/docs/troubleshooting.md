# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## HubSpot write refusals

If a write command with `--apply` says it requires explicit no-snapshot approval when no saved snapshot is available, that is expected in the current Wave 2 safety state.
No HubSpot write was sent.

## OAuth tokens

- If `auth token status` says the token is missing, run:
  - `qwayk-hubspot-safe-agent-cli auth token set --file token.json`
- If your token expires, refresh it using your OAuth process, then run `token set` again.
