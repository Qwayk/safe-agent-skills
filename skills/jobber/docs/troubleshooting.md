# Troubleshooting

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
