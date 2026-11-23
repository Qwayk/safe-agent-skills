# Command reference

Put shared flags before the command name. JSON is the default output.

| Flag | What it does |
| --- | --- |
| `--env-file PATH` | Choose the private settings file. The default is `.env`. |
| `--output json\|text` | Choose how the result is printed. |
| `--timeout-s SECONDS` | Set the timeout for this run. |
| `--config PATH`, `--project-dir DIR` | Choose a JSON project settings file or project folder. |
| `--log-file PATH`, `--verbose`, `--debug` | Set the audit log, show request lines, or show a Python traceback. |
| `--plan-out PATH`, `--plan-in PATH`, `--receipt-out PATH` | Save a preview, apply from it, or choose where the receipt goes. |
| `--apply`, `--ack-no-snapshot`, `--yes` | Apply an approved download, confirm it has no restore point, or confirm a replacement or larger export. |

## Setup

- `unsplash-api-tool --output json --version`
- `unsplash-api-tool onboarding [--no-write-env]`
- `unsplash-api-tool auth check`
- `unsplash-api-tool auth key set --file auth.json`
- `unsplash-api-tool auth key status`

See [setup and common errors](onboarding.md).

## Photos

- `unsplash-api-tool photos list [--page N] [--per-page N] [--order-by latest|oldest|popular]`
- `unsplash-api-tool photos get --id <photo_id>`
- `unsplash-api-tool photos random [--count 1..30] [--query ...] [--username ...] [--orientation ...] [--content-filter low|high]`
- `unsplash-api-tool photos search --query <q> [--page N] [--per-page N] [--order-by relevant|latest]`
- `unsplash-api-tool photos stats --id <photo_id> [--resolution ...] [--quantity ...]`
- `unsplash-api-tool --plan-out plan.json photos download --id PHOTO_ID [--dest PATH] [--overwrite]`
- `unsplash-api-tool --apply --ack-no-snapshot --plan-in plan.json photos download --id PHOTO_ID [--dest PATH]`

To replace an existing file, preview it with `--overwrite` and apply with `--yes` and the same `--overwrite` choice. Omit `--dest` in both commands for tracking only. See [download approvals](safety_model.md).

## Collections

Collection IDs may contain letters, numbers, hyphens, or underscores.

- `unsplash-api-tool collections list [--page N] [--per-page N]`
- `unsplash-api-tool collections get --id <collection_id>`
- `unsplash-api-tool collections photos --id <collection_id> [--page N] [--per-page N] [--orientation ...]`
- `unsplash-api-tool collections related --id <collection_id>`

## Topics

- `unsplash-api-tool topics list [--page N] [--per-page N] [--order-by featured|latest|oldest|position]`
- `unsplash-api-tool topics get --id <topic_slug_or_id>`
- `unsplash-api-tool topics photos --id <topic_slug_or_id> [--page N] [--per-page N] [--orientation ...]`

## Users

- `unsplash-api-tool users get --username <username>`
- `unsplash-api-tool users photos --username <username> [--page N] [--per-page N] [--order-by ...] [--orientation ...]`
- `unsplash-api-tool users likes --username <username> [--page N] [--per-page N] [--order-by ...] [--orientation ...]`
- `unsplash-api-tool users collections --username <username> [--page N] [--per-page N]`
- `unsplash-api-tool users statistics --username <username> [--resolution ...] [--quantity ...]`

## Search

- `unsplash-api-tool search photos --query <q> [--page N] [--per-page N]`
- `unsplash-api-tool search collections --query <q> [--page N] [--per-page N]`
- `unsplash-api-tool search users --query <q> [--page N] [--per-page N]`

## Unsplash statistics

- `unsplash-api-tool stats total`
- `unsplash-api-tool stats month`

## Export result data

An export writes local JSON without recording any photo downloads. Use the shared `--yes` flag when asking for more than one page.

These flags work with each export command.
- `--out <path>` (required)
- `--start-page N` (default 1)
- `--max-pages N` (default 1)
- `--per-page N` (default 10; max 30)
- `--sleep-ms N` (default 0)

- `unsplash-api-tool export photos-search --query <q> [--order-by relevant|latest] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export photos-list [--order-by latest|oldest|popular] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export collections-photos --id <collection_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export topics-photos --id <topic_slug_or_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export users-photos --username <username> [--order-by ...] [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`

## Run history

Commands that can write files or track downloads can save plans, receipts, and a run summary under `.state/runs/` beside the settings file. Use these options to choose where the files go.
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `unsplash-api-tool runs list [--limit 20]`
- `unsplash-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Where the code lives

In `src/unsplash_api_tool/`, `cli.py` wires the commands and `config.py` reads settings. The handlers live in `commands/`. `unsplash_client.py` prepares API calls, and `http.py` sends them and saves photo files. `json_files.py`, `runs.py`, and `audit_log.py` handle local records. `output.py` prints one JSON result per command. See [what was tested](proof.md) before changing the download flow.
