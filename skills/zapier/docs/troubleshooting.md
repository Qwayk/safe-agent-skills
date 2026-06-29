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
  - Store the bearer token in `.env` as `ZAPIER_ACCESS_TOKEN`.
- If your token expires, refresh it using your OAuth process, then run `token set` again.
