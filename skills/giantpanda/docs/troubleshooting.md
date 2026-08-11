# Troubleshooting

Use these checks when a command is blocked.

## auth check and setup

- If `auth check` returns false:
  - run `onboarding`,
  - replace placeholder in `.env`,
  - run `auth check` again.
- `auth check` is local-only.

## Date validation

- `start_date` and `end_date` must be strict `YYYY-MM-DD`.
- `start_date` must be before or equal to `end_date`.
- Invalid dates fail before any network request.

## Add-domain apply blocks

- Add apply requires all four gates:
  - `--apply`
  - `--plan-in`
  - `--approve-plan`
  - `--ack-no-snapshot`
- Apply also needs the exact same `--domain` values used when building the plan.
- `plan_id` mismatch or tampered plan file is a hard refusal.

## Max domain count and formatting

- Maximum domains per add command is 100 raw `--domain` values before sort+dedupe.
- Domains must be valid host names, lowercase normalized, no schemes, paths, ports, wildcard, or spaces.

## Post-write uncertainty

- If the provider response is not JSON, do not retry automatically. Inspect the GiantPanda dashboard or account state manually because the add may already have happened.
- Keep any successful receipt file for manual audit.

## Redirect refusal

The client does not follow redirect responses. Treat a redirect as a provider or endpoint problem and do not resend the token-bearing request to the redirected URL.
