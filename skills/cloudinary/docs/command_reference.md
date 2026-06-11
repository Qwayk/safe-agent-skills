# Command reference

Use this page when you need the exact Cloudinary command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Program name

```bash
cloudinary-safe-agent-cli
```

## Global flags

- `--output {json,text}`: output mode, default `json`
- `--env-file PATH`: choose a different `.env`
- `--config PATH`: optional non-secret JSON config
- `--project-dir PATH`: safe root for `--out`
- `--timeout-s N`: override timeout
- `--verbose`: show HTTP timing on stderr
- `--debug`: raise stack traces instead of clean error output
- `--log-file PATH`: extra audit log path
- `--apply`: attempt a write after review; writes require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available
- `--yes`: second confirmation for writes
- `--plan-out PATH`: save a dry-run plan
- `--plan-in PATH`: apply from an existing plan; approved supported writes validate the plan before applying
- `--receipt-out PATH`: save a receipt when an approved supported command really runs; refusals for missing approval or failed safety checks do not create write receipts
- `--ack-irreversible`: extra confirmation for delete-like actions
- `--run-id ID`: set the local run id
- `--artifacts-dir PATH`: choose the local artifact folder
- `--no-artifacts`: turn off local run artifacts

## Top-level commands

- `--version`
- `onboarding`
- `auth check`
- `runs list`
- `runs show`
- `operations list`
- `operations show`
- `operations <area> <op_key>`

## `onboarding`

```bash
cloudinary-safe-agent-cli onboarding
cloudinary-safe-agent-cli onboarding --no-write-env
```

## `auth check`

```bash
cloudinary-safe-agent-cli --output json auth check
```

## `runs`

```bash
cloudinary-safe-agent-cli --output json runs list --limit 20
cloudinary-safe-agent-cli --output json runs show --run-id 2026-05-25T000000Z_ab12cd
```

## `operations list`

```bash
cloudinary-safe-agent-cli --output json operations list --area upload --limit 20
cloudinary-safe-agent-cli --output json operations list --contains accesskey --include-sensitive
cloudinary-safe-agent-cli --output json operations list --tag beta --include-sensitive
```

Filters:
- `--contains TEXT`
- `--tag TEXT`
- `--method GET|POST|PUT|PATCH|DELETE`
- `--area AREA`
- `--limit N`
- `--include-deprecated`
- `--include-sensitive`

Areas:
- `admin`
- `analyze`
- `live_streaming`
- `permissions`
- `player_profiles`
- `provisioning`
- `upload`
- `video_config`

## `operations show`

```bash
cloudinary-safe-agent-cli --output json operations show --area upload --op upload-signed
```

This returns the shipped metadata for one operation:
- command
- method
- path template
- auth scope
- input style
- sensitivity
- beta or gated flags
- fixed query and form values

## `operations <area> <op_key>`

All explicit Cloudinary commands use the same input flags:
- `--path-param key=value`
- `--query key=value`
- `--form-field key=value`
- `--body-json-file file.json`
- `--multipart-spec-file file.json`
- `--out relative/or/absolute/path`
- `--overwrite`

Examples:

Read asset details:

```bash
cloudinary-safe-agent-cli --output json operations admin \
  resources-get-details-of-a-single-resource-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample
```

Run a read-like Analyze request:

```bash
cloudinary-safe-agent-cli --output json operations analyze analyze-ai-vision-general \
  --body-json-file examples/analyze-ai-vision-general.sample.json
```

Plan a delete:

```bash
cloudinary-safe-agent-cli --output json \
  --plan-out plans/delete-folder.json \
  operations admin folders-delete-folder \
  --path-param folder=archive/old
```

Plan a backup restore:

```bash
cloudinary-safe-agent-cli --output json \
  --plan-out plans/restore-public-id.json \
  operations admin resources-restore-resources-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample-public-id \
  --body-json-file examples/resources-restore-by-public-id.sample.json
```

Attempt a backup restore:

```bash
cloudinary-safe-agent-cli --output json \
  --apply --yes --ack-no-snapshot \
  --plan-in plans/restore-public-id.json \
  operations admin resources-restore-resources-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample-public-id
```

If the reviewed plan still matches, `--ack-no-snapshot` allows the restore to reach Cloudinary and record a receipt.

Download a backed-up version:

```bash
cloudinary-safe-agent-cli --output json \
  --out artifacts/sample-backup.bin \
  --overwrite \
  operations upload download-backup \
  --query public_id=sample-public-id \
  --query version_id=123 \
  --query resource_type=image \
  --query type=upload
```

Attempt that delete:

```bash
cloudinary-safe-agent-cli --output json \
  --apply --yes --ack-irreversible --ack-no-snapshot \
  --plan-in plans/delete-folder.json \
  operations admin folders-delete-folder \
  --path-param folder=archive/old
```

If the reviewed plan still matches, the tool can send the destructive write after both acknowledgements and then record a receipt.

Save a sensitive read:

```bash
cloudinary-safe-agent-cli --output json \
  --project-dir . \
  operations live_streaming getlivestreams \
  --out artifacts/live-streams.json
```
