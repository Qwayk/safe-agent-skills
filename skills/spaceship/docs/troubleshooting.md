# Troubleshooting

Start here when the tool does not connect, the output looks wrong, or the agent says it is blocked.

## Connection problems

Most connection issues come from missing settings, the wrong key type, expired access, or account permissions.

Ask your agent:

- “Check the connection and explain the problem in plain language.”
- “Tell me which setting is missing, but do not print any secret value.”

## Request details

Use `--verbose` only when you need to see request start and end lines.

Secrets must never be printed. That includes the API key, API secret, transfer authorization code, and private contact or transaction values.

## Error details

By default, the tool prints one structured error. That keeps the output easy for agents to read.

If you are debugging the code itself, add `--debug` to see a full Python stack trace.

## Typical causes

- If a provider read or apply refuses to start, check `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET`.
- The production base is fixed to `https://spaceship.dev/api`; the CLI does not accept another provider host.
- If calls pause with rate limit output, use `rate_retry_after_seconds` from output before retrying.
- If a write refuses, read the `reasons` and compare the current command, body digest, snapshot, and required acknowledgements with the saved plan.
- If a response says `accepted_not_completed`, use the async operation ID with `async-operations status` instead of treating the request as finished.
