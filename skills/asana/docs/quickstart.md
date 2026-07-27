# Get the first useful Asana result

Start by confirming who the token belongs to and which workspaces that user can see. These reads do not change Asana.

```bash
.venv/bin/asana-safe --env-file .env auth check
.venv/bin/asana-safe --env-file .env api get-workspaces
```

The first command returns a bounded current-user identity. The second returns visible workspaces. If both succeed, ask your agent to choose the correct workspace and explain what it can review there.

## Inspect a fixed command

List commands by family or show the exact path, parameters, OAuth scopes, body type, and risk classification for one command:

```bash
.venv/bin/asana-safe commands list --family Tasks
.venv/bin/asana-safe commands show get-tasks-for-project
```

## Read project tasks

Replace the placeholder GID with a real project GID returned by Asana:

```bash
.venv/bin/asana-safe --env-file .env api get-tasks-for-project \
  --param project_gid=1200000000000001 \
  --param opt_fields=gid,name,assignee.name,due_on,completed \
  --paginate \
  --max-pages 5
```

Only documented parameters are accepted. Pagination stops at the chosen page limit and reports how many pages were fetched.

## Prepare an update without changing Asana

Asana JSON write bodies use a top-level `data` object. This command reads the current task when possible and saves a plan; it does not send the update:

```bash
.venv/bin/asana-safe --env-file .env api update-task \
  --param task_gid=1200000000000002 \
  --data-json '{"data":{"name":"Review launch checklist","due_on":"2026-08-03"}}'
```

The output gives you the exact plan path and plan ID. Review the target, request body, before-state, risk, and verification method. The tool also creates a private local signing key under `.state/`; the key stays outside the plan.

## Apply the reviewed plan

Use only the saved plan during apply; do not repeat parameters or the body:

```bash
.venv/bin/asana-safe --env-file .env api update-task \
  --plan-in .state/plans/PLAN_ID.json \
  --apply \
  --approve PLAN_ID
```

Add `--acknowledge-no-snapshot` only when the plan says no reliable before-state exists. Add `--acknowledge-risk` only when the plan classifies the operation as requiring stronger approval. The receipt is saved under `.state/receipts/` unless you choose `--receipt-out`.

Apply uses the signing key beside the same env file. If that key is missing or changed, or if the plan was created by an older unsigned version, create and review a new plan instead of trying to repair the saved JSON.

For asynchronous exports, duplication, templates, or other job-backed work, `--wait` polls a returned Asana job when the response includes a job GID. Otherwise the receipt reports that the request was accepted or started but not proved complete.
