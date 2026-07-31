# Configuration

The tool reads local settings from `.env` by default.

## Required `.env` keys

- `PORKBUN_API_KEY` (required for authenticated calls)
- `PORKBUN_SECRET_API_KEY` (required for authenticated calls)
- `PORKBUN_API_HOST` (`default` or `ipv4`)
- `PORKBUN_TIMEOUT_S` (optional, default `30`)

## Host modes

Use one of:
- `default` (default) → `https://api.porkbun.com/api/json/v3`
- `ipv4` → `https://api-ipv4.porkbun.com/api/json/v3`

## Environment file

1. Copy `.env.example` to `.env`.
2. Fill the required values.
3. Keep `.env` out of version control.

## Command use

- Any command can set a custom file path with `--env-file`.
- Example:
  `porkbun --env-file ./secrets/porkbun.env auth check`

## Secret handling

- Keys are never printed.
- Secret-bearing command results are redacted on stdout and text/JSON output.
- Use `--ack-secret` together with `--secret-out` to persist full secret-bearing results to a preflighted owner-only file.
- Secret destinations are checked before a provider request and written atomically as `0600`; invalid, directory, unwritable, and symbolic-link targets are refused.
- Tool-owned `.state` directories are `0700`. The plan-signing key, plans, and receipts are `0600`.
- Plan, receipt, and secret outputs must use separate paths and must not alias the environment file, JSON input, or plan input. Collisions are refused before a provider request or replacement.

## Local plan signing key

The first saved plan creates `.state/plan-signing.key`. Creation is concurrency-safe and never overwrites an existing key, so simultaneous first plans all use the same winning key. The key authenticates the complete plan, including its operation, target, inputs, expiry, idempotency key, snapshot state, and cost data.

Keep the key private and keep the same working-directory `.state` for plan and apply. If the key is missing, malformed, not owner-only, or does not match the plan signature, apply stops before a provider request.

## File-only invite token

For invite status, put the token in a JSON file:

```json
{
  "token": "REDACTED"
}
```

Then run `porkbun account get-account-invite-status --input ./invite-status.json`. The command does not accept `--token`.
