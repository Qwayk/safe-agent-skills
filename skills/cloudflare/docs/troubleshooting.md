# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## “It looks hung” (slow endpoints)

Some Cloudflare surfaces (commonly Zero Trust) can be very slow in some accounts.

Try:
- Add `--progress` to print periodic "still waiting" messages to stderr.
- Use `--timeout-profile slow` (or increase `--read-timeout-s`).
- Run `cloudflare-api-tool auth doctor` to get a quick read-only latency report.

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Writes and sensitive reads (safety gates)

- **Writes** are preview-first. The tool will refuse to write unless you explicitly approve the apply step (and for risky/batch changes, an extra confirmation).
- **Sensitive reads** (like downloading script code or reading KV values) are also gated and are only allowed when writing to an explicit local output file.
- Sensitive read output is restricted to be **under your project directory** (so you don’t accidentally write to unexpected locations).

## Cloudflare tokens / permissions

- If `auth check` fails:
  - Confirm `CLOUDFLARE_API_TOKEN` is set in your `--env-file`.
  - Confirm the token has permissions for the endpoint you called (see `docs/onboarding.md`).
- If `auth check` succeeds but `d1 databases list` fails:
  - Your token likely lacks D1 database permissions (the Cloudflare API may return an “authentication error” even though the token is valid).
  - Run `cloudflare-api-tool auth probe` to confirm.
- If you see rate limits (HTTP 429):
  - Re-run with `--verbose` to confirm which endpoints were called and slow down your polling.

## Operations / jobs (advanced)

- `operations <area> <op_key>` and `jobs run` use the tool’s shipped coverage ledgers as their operation index:
  - `docs/api_coverage_workers_platform.md`
  - `docs/api_coverage_zero_trust.md`

## “Refused” vs “blocked” (what it means)

- **Blocked** usually means setup is missing (no token, wrong base URL) or Cloudflare denied the request (permissions). Nothing was changed.
- **Refused** means the tool intentionally did nothing because the request was unsafe or ambiguous. This is a safety feature.
