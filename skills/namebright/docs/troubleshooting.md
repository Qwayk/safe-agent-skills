# Troubleshooting

Start here when the tool does not connect, the output looks wrong, or the agent says it is blocked.

## Connection problems

Most connection issues come from missing settings, the wrong key type, expired access, or account permissions.

Ask your agent:

- “Check the connection and explain the problem in plain language.”
- “Tell me which setting is missing, but do not print any secret value.”

## Request details

Use `--verbose` only when you need to see request start and end lines.

Secrets must never be printed. That includes Authorization headers, keys, and tokens.

## Error details

By default, the tool prints one structured error. That keeps the output easy for agents to read.

## OAuth tokens

- Run connection checks and token refresh by re-reading credentials:
  - `namebright-safe-cli auth check`
  - `namebright-safe-cli auth token`
- If any secret changed, update `.env` and rerun onboarding before retrying.
