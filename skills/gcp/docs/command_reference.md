# Command reference

Use the command reference when you already know the Google Cloud job and need the exact service, operation, input file shape, and safety flags.

For the guided path, start with [What this skill can help you do](use_cases.md), [Set up your Google Cloud access](onboarding.md), and [See how this skill stays safe](safety_model.md).

## Global flags

These flags apply across the CLI:

- `--config CONFIG`
- `--project-dir PROJECT_DIR`
- `--output json|text`
- `--version`
- `--env-file .env`
- `--timeout-s TIMEOUT_S`
- `--verbose`
- `--debug`
- `--quota-project QUOTA_PROJECT_ID`
- `--run-id RUN_ID`
- `--artifacts-dir ARTIFACTS_DIR`
- `--no-artifacts`
- `--plan-out plan.json`
- `--plan-in plan.json`
- `--apply`
- `--yes`
- `--ack-no-snapshot`
- `--ack-irreversible`
- `--output-file result.json`
- `--log-file audit.jsonl`

## Get connected

Use these commands to create local setup files or check basic runtime details.

- `qwayk-gcp-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-gcp-safe-agent-cli --output json --version`

## Check access

Use this command to confirm ADC.

- `qwayk-gcp-safe-agent-cli auth check`

## Inventory and runs

- `qwayk-gcp-safe-agent-cli --output json inventory summary`
- `qwayk-gcp-safe-agent-cli runs list [--limit 20]`
- `qwayk-gcp-safe-agent-cli runs show --run-id 2026-01-19T104512Z_a3f91c`

## How to find the right generated operation

Generated GCP commands use this shape:

```bash
qwayk-gcp-safe-agent-cli <service> <operation> --input-json input.json
```

The `<service>` is the Google Cloud API family, such as `compute`, `serviceusage`, `storage`, `run`, `sqladmin`, `logging`, or `cloudbilling`. The `<operation>` is the generated operation name from [API coverage](api_coverage.md).

Use this flow when you know the cloud job but not the command yet:

1. Run `qwayk-gcp-safe-agent-cli --help` to see included services.
2. Search [API coverage](api_coverage.md) for the service or resource name, such as `instances-list`, `services-list`, `buckets-list`, `projects-locations-services-list`, `entries-list`, or `billing-accounts-list`.
3. Copy the exact operation name from the coverage table.
4. Create `input.json` with the path values the operation needs, plus any query or body fields.
5. Start with a read. For writes, save a dry-run plan first and review it before apply.

Common first checks:

| Job | Service | Operation to look for | Typical path values |
|---|---|---|---|
| List Compute Engine instances | `compute` | `instances-list` | `project`, `zone` |
| Check enabled services | `serviceusage` | `services-list` | `parent` such as `projects/PROJECT_ID` |
| List Cloud Storage buckets | `storage` | `buckets-list` | `project` |
| List Cloud Run services | `run` | `projects-locations-services-list` | `parent` such as `projects/PROJECT_ID/locations/REGION` |
| List Cloud SQL instances | `sqladmin` | `instances-list` | `project` |
| Read Cloud Logging entries | `logging` | `entries-list` | `body` with `resourceNames`, filters, and page size |
| Check billing accounts | `cloudbilling` | `billing-accounts-list` | usually query fields only |

When the path values are not obvious, search the operation row in `docs/api_coverage.md`, then compare the path template shown in the evidence column with the official reference linked from `docs/references.md`.

## Generated service commands

Every Discovery operation is exposed as an explicit `service operation` command.

Examples:

- `qwayk-gcp-safe-agent-cli compute instances-list --input-json input.json`
- `qwayk-gcp-safe-agent-cli serviceusage services-list --input-json input.json`
- `qwayk-gcp-safe-agent-cli storage buckets-list --input-json input.json`

The input JSON usually carries `path`, `query`, and `body` values. For example:

```json
{
  "path": {
    "project": "proj-a",
    "zone": "us-central1-a"
  },
  "query": {
    "maxResults": 10
  }
}
```

Reads can run without `--apply`. Writes default to dry-run and only go live after a reviewed plan.

## Plan and apply

Write-capable commands always start with a plan.

- Dry-run: `qwayk-gcp-safe-agent-cli compute instances-delete --input-json input.json --plan-out plan.json`
- Apply: `qwayk-gcp-safe-agent-cli --apply --yes --plan-in plan.json --ack-no-snapshot --ack-irreversible compute instances-delete --input-json input.json`

Use `--ack-no-snapshot` for high-risk or no-snapshot writes and `--ack-irreversible` when the operation cannot be undone safely.

## Batch work

This source build does not ship a separate CSV batch runner yet.

For repeated work, prepare one reviewed generated command plan at a time, or add a future batch runner that expands into explicit generated `service operation` commands instead of a generic bridge.
