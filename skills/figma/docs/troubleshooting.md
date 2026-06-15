# Troubleshooting

When Figma stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading files, projects, comments, components, and design metadata, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Figma error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
