# Troubleshooting

When Jobber stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing clients, requests, quotes, jobs, invoices, and field-service records, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Jobber error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## First clue

Start here when the tool does not connect or the tool refuses an action.

## Common setup issues

- Missing `.env` values:
  - Run `auth check` and review `token_available` and `missing_token`.
- Wrong file location:
  - Pass `--env-file` for non-default locations.
- Missing OAuth app values:
  - Add `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET`, `JOBBER_REDIRECT_URI` to `.env`.

## Auth and token issues

- If auth is blocked, rerun:
  - `qwayk-jobber-safe-agent-cli auth token status`
  - `qwayk-jobber-safe-agent-cli auth check`
- If token refresh fails, confirm `CLIENT_SECRET` and token file scope are still current.
- If refresh requires approval in your process, run refresh only with `--apply --yes`.

## Command and API issues

- `Missing access token` or token check errors:
  - Store token via `auth token set --file token.json` and run again.
- Unknown action or missing plan:
  - Verify command name against `schema queries` or `schema mutations` and `docs/api_coverage.md`.
- Write refusal:
  - Apply with `--apply --yes --plan-in <reviewed-plan.json>` after reviewing the plan.

## Runtime and limits

- Rate-limits:
  - Jobber enforces request and GraphQL cost limits.
  - Retry after a short backoff when the provider asks for it.
- Webhooks:
  - Verify signatures with `webhooks verify-signature`.
  - Duplicate webhook deliveries are possible because delivery is at-least-once.

## Verbosity for debugging

- Use `--verbose` to view request-level logging.
- Use `--debug` when you need stack traces.
- Never run with secrets in debug output.
