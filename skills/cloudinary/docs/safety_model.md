# Safety model

This tool is safe by default.

## Default rule

Read commands run directly.
Write commands return a dry-run plan unless you add `--apply`.
When no saved snapshot is available, current write apply requires explicit no-snapshot approval before Cloudinary credentials are used for the write or Cloudinary HTTP.

## Write confirmations

All writes need:
- `--apply`
- `--yes`

Delete-like commands and access-key commands also need:
- `--ack-irreversible`

## Recovery boundary

There is no generic rollback or snapshot endpoint in this tool.
Backup and restore endpoints are explicit operations, not a blanket safety layer for other writes:
- `operations upload download-backup` is a read that downloads a backed-up version.
- `operations admin resources-restore-resources-by-public-id` and `operations admin resources-restore-resources-by-asset-id` are writes, and they require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available.
- `operations admin resources-delete-backed-up-versions-of-a-resource` is destructive, so it also requires `--ack-irreversible` plus `--ack-no-snapshot` when no saved snapshot is available.

## Plan and apply files

For writes, the safe path is:
1. run the command without `--apply`
2. review the returned plan
3. attempt apply with `--apply --yes --plan-in <plan.json> --ack-no-snapshot`
4. keep the receipt or refusal output and local run proof

The plan stores:
- target operation
- method and resolved path
- query
- auth scope
- environment fingerprint
- `before_state.required: true`, `before_state.supported: false`, and `before_state.status: no_snapshot_available`
- explicit `recovery` metadata showing that no backup was saved by this write path

On apply, the tool first refuses if the plan target, path, query, or environment fingerprint do not match the current request. After those gates pass, supported writes can reach Cloudinary and emit a receipt. If `--ack-no-snapshot` is missing, the tool still refuses safely before the write.

## Sensitive and binary output

Some Cloudinary results must not print to stdout.
These need `--out`:
- access key reads and write results
- live streaming reads and write results
- archive download URL style write results
- binary backup endpoints like `operations upload download-backup`

Dry-run plans do not need `--out`.
Real reads and apply attempts do.

## Safe output paths

`--out` must stay inside `--project-dir`.
The tool refuses directory escape and accidental overwrite unless you add `--overwrite`.

## Secret handling

The tool redacts loaded secret values from errors and audit logs.
It never prints secrets on purpose.

## Local proof

Write-capable runs create local artifacts under `.state/runs/` next to the active `--env-file`.
That gives you:
- `plan.json` for dry-runs
- `receipt.json` for successful applies
- `audit.jsonl`
- `summary.md`
- a shared `index.jsonl` for `runs list` and `runs show`
