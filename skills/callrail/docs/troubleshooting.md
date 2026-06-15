# Troubleshooting

When CallRail stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing calls, forms, companies, trackers, and attribution data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the CallRail error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
