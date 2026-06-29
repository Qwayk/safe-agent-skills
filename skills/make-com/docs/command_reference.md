# Command reference

## Run command

```bash
make-com-safe [global flags] <command>
```

## Global flags

- `--output {json,text}`
- `--env-file FILE` (default `.env`)
- `--config FILE`, `--project-dir DIR`
- `--timeout-s SECONDS`
- `--verbose`, `--debug`
- `--log-file FILE`, `--no-artifacts`, `--artifacts-dir DIR`, `--run-id ID`
- `--apply`, `--yes`
- `--plan-out FILE`, `--plan-in FILE`, `--receipt-out FILE`
- `--ack-no-snapshot`, `--ack-irreversible`

## Top-level commands

### `runs`

Local audit and history.

```bash
make-com-safe runs list [--limit 20]
make-com-safe runs show --run-id <id>
```

### `onboarding`

```bash
make-com-safe onboarding [--no-write-env]
```

- `--no-write-env` prints guidance only and does not write `.env`.

### `auth`

```bash
make-com-safe auth check
make-com-safe auth token set --file PATH
make-com-safe auth token status
```

### `api`

Officially scoped Make API commands.

```bash
make-com-safe api list
make-com-safe api schema <family> <operation>
make-com-safe api <family> <operation> [--path-param key=value] [--query key=value] [--body-json JSON] [--body-file PATH]
```

Examples:

```bash
make-com-safe api list
make-com-safe api schema scenarios list-scenarios
make-com-safe api scenarios list-scenarios --query "teamId=123"
make-com-safe api scenarios update-scenario --path-param scenarioId=123 --body-json '{"status":"disabled"}'
```

## Write flow for API operations

The following flow is required for writes:

The saved plan records the Make base URL, a one-way credential fingerprint, and non-secret target fingerprints. Apply refuses if the credential, target path/query inputs, or request body differs from the reviewed plan.

1. Create/inspect a plan:

```bash
make-com-safe --plan-out /tmp/plan.json api <family> <write-op> ...
```

2. Apply only with a reviewed plan:

```bash
make-com-safe --plan-in /tmp/plan.json --apply --yes api <family> <write-op> ...
```

3. Add additional safety flags for specific risk types:

```bash
make-com-safe --plan-in /tmp/plan.json --apply --yes --ack-no-snapshot --ack-irreversible --receipt-out /tmp/receipt.json api <family> <write-op> ...
```

## Parameter binding

- `--path-param` is repeated for path placeholders.
- `--query` is repeated for query-string values.
- `--body-json` is inline JSON.
- `--body-file` reads JSON from file.
- If no-JSON body is required, use only `--path-param` and `--query`.
- Stored command history redacts raw `--body-json` values, `--body-file` paths, and secret-looking `--path-param` / `--query` values.

## Notes

- Command and operation names are from `api list` and `api schema`; operation names are not free-form.
- Base URL is set by `MAKE_BASE_URL` and normalized to `/api/v2`.
