# Troubleshooting

## Auth and setup

- `auth check` returns `"ok": false` when token is missing or the live probe fails.
  - For `personal`/`oauth`, this usually means token setup or permission is blocked.
  - For `plan`, probe is skipped by design and success depends on token presence.
- If token file mode is used, run:

```bash
figma-safe-agent-cli auth token set --file token.json
figma-safe-agent-cli auth token status
```

- If auth still blocks, verify the `auth_mode` and token ownership in your Figma org/project settings.

## Operation and query issues

- Use the explicit named flags shown in the operation metadata.
- Required path/query flags must be present before execution.
- `--version-id` is used for the Figma `version` query parameter.
- Missing required fields return clear validation errors before any network call.
- For `--plan-in`, use a plan created from the same command and review mode.

## Dry-run and apply

- If a write seems to apply immediately, check if `--apply` is set.
- If `--apply` is missing, writes should return `"dry_run": true`.
- For risky writes, confirm `--yes` and `--ack-irreversible` requirements are shown in the plan.
- If a fully gated write returns `"refused": true` with `before-state`, that is the current safe behavior. No provider write happened.

## Debug output

- `--verbose` prints request timing logs to stderr.
- `--output json` keeps a machine-readable single-object response.
- `--debug` adds stack traces for developer-level failures.
