# Command reference

The executable is `qwayk-spaceship-safe-agent-cli`. It exposes 40 fixed operation commands, plus local onboarding, auth checking, version, and run-history commands. Provider work is available only through those named operations.

## Meta commands

- `qwayk-spaceship-safe-agent-cli --output json --version`
- `qwayk-spaceship-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-spaceship-safe-agent-cli auth check`

## Safe write flow (shared flags)

Write-capable commands use these global flags:

- `--plan-out <path>`: write a dry-run plan JSON and print it.
- `--plan-in <path>`: apply from a previously reviewed plan.
- `--receipt-out <path>`: write a JSON receipt on apply.
- `--apply`: enable live execution.
- `--yes`: required with `--apply`.
- `--ack-spend`: acknowledge spend/cost side effects.
- `--ack-ownership`: acknowledge ownership-sensitive changes.
- `--ack-dns-risk`: acknowledge DNS-risk changes.
- `--ack-financial`: acknowledge financial/billing side effects.
- `--ack-destructive`: acknowledge destructive changes.
- `--ack-private-data`: acknowledge private-personal-data handling.
- `--ack-no-snapshot`: acknowledge that no reliable state snapshot or required full financial recheck exists.

Required pattern:

```bash
qwayk-spaceship-safe-agent-cli --output json --plan-out my-plan.json domains create example.com --body-file body.json
qwayk-spaceship-safe-agent-cli --output json --apply --yes --plan-in my-plan.json --ack-spend --ack-ownership domains create example.com --body-file body.json
```

If no output path is supplied, a normal write plan is saved at `.state/runs/<run_id>/plan.json` and a successful apply receipt at `.state/runs/<run_id>/receipt.json`. Explicit paths override these defaults.

## Run history

- `qwayk-spaceship-safe-agent-cli runs list [--limit 20]`
- `qwayk-spaceship-safe-agent-cli runs show --run-id <run_id>`

Use a short local name such as `renewal-review` for `--run-id`. It must be one non-empty path segment; absolute paths, slashes, backslashes, `.` and `..` are refused. Run history keeps normal domain targets readable but shows contact IDs and SafePay transaction IDs as deterministic SHA-256 values.

## API commands by surface

- `qwayk-spaceship-safe-agent-cli async-operations status <operationId>`
- `qwayk-spaceship-safe-agent-cli contacts get <contact>`
- `qwayk-spaceship-safe-agent-cli contacts save --body-file body.json`
- `qwayk-spaceship-safe-agent-cli contacts attributes get <contact>`
- `qwayk-spaceship-safe-agent-cli contacts attributes set --body-file body.json`
- `qwayk-spaceship-safe-agent-cli dns delete-records <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli dns list-records <domain> [--take N] [--skip N] [--order-by type|-type|name|-name]` — `take` 1–500
- `qwayk-spaceship-safe-agent-cli dns set-records <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains check-availability <domain>`
- `qwayk-spaceship-safe-agent-cli domains check-domains --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains delete <domain>` — local HTTP-501 refusal; no network request
- `qwayk-spaceship-safe-agent-cli domains list [--take N] [--skip N] [--order-by expirationDate|-expirationDate]` — `take` 1–100; other official name, Unicode-name, and registration-date values are also accepted
- `qwayk-spaceship-safe-agent-cli domains get <domain>`
- `qwayk-spaceship-safe-agent-cli domains create <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains renew <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains restore <domain>`
- `qwayk-spaceship-safe-agent-cli domains set-autorenew <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains set-contacts <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains set-nameservers <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains set-email-protection <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains set-privacy <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains transfer get <domain>`
- `qwayk-spaceship-safe-agent-cli domains transfer auth-code <domain>`
- `qwayk-spaceship-safe-agent-cli domains transfer request <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains transfer lock <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli domains personal-nameservers delete-host <domain> <currentHost>`
- `qwayk-spaceship-safe-agent-cli domains personal-nameservers list <domain>`
- `qwayk-spaceship-safe-agent-cli domains personal-nameservers get-host <domain> <currentHost>` — local HTTP-501 refusal; no network request
- `qwayk-spaceship-safe-agent-cli domains personal-nameservers update-host <domain> <currentHost> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli sellerhub delete-domain <domain>`
- `qwayk-spaceship-safe-agent-cli sellerhub list-domains [--take N] [--skip N]` — `take` 1–100
- `qwayk-spaceship-safe-agent-cli sellerhub list-sold-domains [--take N] [--cursor <cursor>] [--sale-date-time-from <timestamp>] [--sale-date-time-to <timestamp>]` — `take` defaults to 100 and is limited to 1–100; continuation is returned as `cursor`
- `qwayk-spaceship-safe-agent-cli sellerhub get-domain <domain>`
- `qwayk-spaceship-safe-agent-cli sellerhub safepay list [--take N] [--skip N]` — `take` 1–100
- `qwayk-spaceship-safe-agent-cli sellerhub safepay get <transactionId>`
- `qwayk-spaceship-safe-agent-cli sellerhub verification-records`
- `qwayk-spaceship-safe-agent-cli sellerhub update-domain <domain> --body-file body.json`
- `qwayk-spaceship-safe-agent-cli sellerhub create-checkout-link --body-file body.json`
- `qwayk-spaceship-safe-agent-cli sellerhub create-domain --body-file body.json`
- `qwayk-spaceship-safe-agent-cli sellerhub safepay create --body-file body.json`

The required acknowledgement flags depend on the operation and whether Spaceship exposes a reliable current-state or financial check. Create the plan first and use the exact list in `required_acknowledgements`.

Every command maps to one row in the [API coverage ledger](api_coverage.md).
