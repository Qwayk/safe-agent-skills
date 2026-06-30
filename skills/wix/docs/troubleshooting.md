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

If you are debugging the code itself, add `--debug` to see a full Python stack trace.

## OAuth tokens

- If `auth token status` says the token is missing, run:
  - `wix-safe-agent-cli auth token set --file token.json`
- If your token is expired, run `wix-safe-agent-cli auth token create` again, or for older legacy Wix apps run `wix-safe-agent-cli auth token refresh`.
- If `auth check` reports token validation errors, run `wix-safe-agent-cli auth token inspect --token ...` to confirm active state and claims.
