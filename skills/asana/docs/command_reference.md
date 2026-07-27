# Command reference

`asana-safe` exposes 248 fixed operation commands generated from the pinned official Asana REST specification. The CLI never accepts an HTTP method, URL, relative API path, or arbitrary batch entry.

## Global flags

Put global flags before the command:

```text
--env-file PATH       Secret env file; default .env
--output json|text    Output mode; JSON emits one object
--timeout-s SECONDS   Positive request timeout override
--verbose             Request method, official path, status, and timing on stderr
--debug               Local Python traceback on stderr
--log-file PATH       Optional redacted JSONL audit log
--version             Version JSON without auth
```

## Setup and connection

```bash
asana-safe --env-file .env onboarding
asana-safe --env-file .env auth check
```

`onboarding --no-write-env` prints setup without creating `.env`.

## Browse fixed commands

```bash
asana-safe commands list
asana-safe commands list --family Tasks
asana-safe commands list --method GET
asana-safe commands list --writes-only
asana-safe commands show update-task
```

`commands show` returns the official operation ID, method, fixed path, documented parameters, request media type, OAuth scopes, access notes, risk class, snapshot/readback candidates, pagination, and asynchronous classification.

## Run a read

```bash
asana-safe --env-file .env api COMMAND --param NAME=VALUE
```

Repeat `--param` for documented path and query parameters. Unknown, duplicate, missing required, or invalid enum/number/boolean parameters are refused. Example:

```bash
asana-safe --env-file .env api get-tasks-for-project \
  --param project_gid=1200000000000001 \
  --param opt_fields=gid,name,due_on,completed
```

For documented offset lists:

```text
--paginate --max-pages N
```

Pagination stops on no next offset, an empty page, or the chosen positive page limit.

## Prepare a JSON write

Use either an exact JSON string or a JSON file. Asana write bodies use a top-level `data` object:

```bash
asana-safe --env-file .env api update-task \
  --param task_gid=1200000000000002 \
  --data-json '{"data":{"name":"Review launch checklist"}}'

asana-safe --env-file .env api create-task --data-file examples/create-task.body.json
```

The command saves a schema-2 plan, returns its path and ID, and authenticates it with a private local key outside the plan. It does not send the write.

## Prepare an attachment

The fixed attachment operation accepts documented multipart fields only:

```bash
asana-safe --env-file .env api create-attachment-for-object \
  --data-json '{"parent":"1200000000000002"}' \
  --file file=./brief.pdf
```

The plan records the file name, size, and SHA-256 hash. Apply refuses if the file changed. The App Components-only `connect_to_app` field is refused.

## Apply a reviewed plan

```bash
asana-safe --env-file .env api COMMAND \
  --plan-in .state/plans/PLAN_ID.json \
  --apply \
  --approve PLAN_ID
```

Do not repeat `--param`, `--data-json`, `--data-file`, or `--file`. Apply verifies the plan's local signature before HTTP, then reconstructs and revalidates the fixed request and safety fields instead of trusting editable JSON. The signing key must be available beside the same selected env file. Unsigned, schema-1, edited, or differently signed plans must be recreated.

When named by the plan, add:

```text
--acknowledge-no-snapshot   Accept that no reliable before-state exists
--acknowledge-risk          Accept the plan's stronger-risk reasons
```

Optional apply flags:

```text
--receipt-out PATH
--wait
--wait-timeout-s SECONDS
--poll-interval-s SECONDS
```

`--wait` polls `/jobs/{job_gid}` only when an asynchronous result includes a job GID. Otherwise the receipt keeps the state unverified and points the user to the fixed status command for that resource.

## Complete command inventory

The generated [API coverage ledger](api_coverage.md) lists every official path and operation ID, its fixed command or exclusion, risk/access class, and live-proof status.
