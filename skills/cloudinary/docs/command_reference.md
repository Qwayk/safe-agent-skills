# Command reference

Start with [Quickstart](quickstart.md) for a first read and [Connect Cloudinary](onboarding.md) for settings.

## Options before the command

| Option | What it does |
| --- | --- |
| `--version` | Show the installed tool version. |
| `--output json\|text` | Choose JSON or text. JSON is the default. |
| `--env-file PATH` | Choose a settings file. |
| `--config PATH`, `--project-dir PATH` | Load non-secret settings for wrappers or choose the root for `--out`. |
| `--timeout-s N`, `--verbose`, `--debug` | Set the request timeout, show timing, or show a stack trace. |
| `--log-file PATH` | Add a local audit log. |
| `--plan-out PATH` | Save a preview. |
| `--plan-in PATH`, `--apply`, `--yes` | Apply the matching plan after approval. |
| `--ack-no-snapshot`, `--ack-irreversible` | Record approval to proceed without a saved copy and for commands that require extra confirmation. |
| `--receipt-out PATH` | Pick where to save the write receipt. |
| `--run-id ID`, `--artifacts-dir PATH`, `--no-artifacts` | Choose the run ID, storage folder, or turn off automatic run files. |

## Find a command

- `onboarding [--no-write-env]` guides setup.
- `auth check` checks the configured connections.
- `runs list [--limit N]` and `runs show --run-id ID` find saved records.
- `operations list` lists the supported commands.
- `operations show --area AREA --op COMMAND` shows the exact options, request format, and access needed.
- `operations <area> <op_key>` runs a named operation.

Use `--contains`, `--tag`, `--method`, `--area`, or `--limit` to filter the list. Use `--include-deprecated` or `--include-sensitive` to include those entries. The areas are `admin`, `analyze`, `live_streaming`, `permissions`, `player_profiles`, `provisioning`, `upload`, and `video_config`.

```bash
cloudinary-safe-agent-cli --output json operations list --area upload --limit 20
cloudinary-safe-agent-cli --output json operations show --area upload --op upload-signed
```

## Options after the command

Use the options shown for that operation. Values in the endpoint path use `--path-param key=value`. Other URL options use `--query key=value`. For a request body, follow the listed format and use `--form-field key=value`, `--body-json-file PATH`, or `--multipart-spec-file PATH`. Use one body format for each operation. A multipart upload can include files and form fields.

Put `--out PATH` after the operation to save its output inside `--project-dir`. Use `--overwrite` there only to replace that local file. Cloudinary's upload setting `overwrite` controls whether an existing asset can be replaced.

## Read one asset

```bash
cloudinary-safe-agent-cli --output json operations admin \
  resources-get-details-of-a-single-resource-by-public-id \
  --path-param resource_type=image --path-param type=upload --path-param public_id=sample
```

Run an Analyze request using [the sample input](../examples/analyze-ai-vision-general.sample.json).

```bash
cloudinary-safe-agent-cli --output json operations analyze analyze-ai-vision-general \
  --body-json-file examples/analyze-ai-vision-general.sample.json
```

## Restore a backed-up asset

Open the asset and confirm the backup version before choosing a restore. The preview and apply use the same JSON file.

```bash
cloudinary-safe-agent-cli --plan-out plans/restore-public-id.json \
  operations admin resources-restore-resources-by-public-id \
  --path-param resource_type=image --path-param type=upload \
  --body-json-file examples/resources-restore-by-public-id.sample.json
```

After approval, pass the plan with `--plan-in plans/restore-public-id.json --apply --yes --ack-no-snapshot` before the same operation and inputs. Use [the approval guide](safety_model.md) for deletes, replacements and access-key changes.

To download a version without restoring, use the asset ID and version ID from the asset's backup details. [Cloudinary backup download](https://cloudinary.com/documentation/image_upload_api_reference#download_backup)

```bash
cloudinary-safe-agent-cli --output json operations upload download-backup \
  --query asset_id=ASSET_ID --query version_id=VERSION_ID --out artifacts/sample-backup.bin
```

To save a private stream result:

```bash
cloudinary-safe-agent-cli --output json --project-dir . \
  operations live_streaming getlivestreams --out artifacts/live-streams.json
```
