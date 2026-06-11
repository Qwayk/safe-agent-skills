# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets are redacted in tool output (`Authorization` is never printed).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Auth check

If `auth check` fails with a missing token message, set `CALLRAIL_API_TOKEN` in your `.env` and re-run:

```bash
qwayk-callrail-safe-agent-cli auth check
```

Common causes after setup:

- wrong `CALLRAIL_API_BASE_URL`
- typo in the token
- token not enabled for the called operation

Write calls can fail with permission errors when the key is read-only.

## Command not found errors

The tool includes only these command groups:
- `onboarding`
- `auth check`
- `runs list|show`
- `accounts`, `calls`, `tags`, `companies`, `form-submissions`, `integrations`, `integration-filters`, `notifications`, `outbound-caller-ids`, `page-views`, `sms-threads`, `summary-emails`, `text-messages`, `message-flows`, `trackers`, `users`, `leads`, `lead-timelines`

If you copied an older example and the parser rejects it, compare it against `docs/command_reference.md` and `docs/api_coverage.md`.
