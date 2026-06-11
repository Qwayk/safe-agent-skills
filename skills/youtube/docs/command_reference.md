# Command reference

Use this page when you need the exact YouTube command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do with YouTube](use_cases.md), [Connect your YouTube account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `youtube-api-tool onboarding [--no-write-env]`

## Auth

- `youtube-api-tool --output json --version`
- `youtube-api-tool auth check`
- `youtube-api-tool auth login --console` (plan/refusal; does not run OAuth or write token state yet)
- `youtube-api-tool auth token set --file token.json` (plan/refusal; does not write token state yet)
- `youtube-api-tool auth token status`
- `youtube-api-tool auth token show-safe`

## Methods (pinned discovery)

- `youtube-api-tool methods list [--resource <resource-prefix>]`

## API (explicit per-method commands)

- Plan-only (no network; safe default):
  - `youtube-api-tool api <resource.method> [--params-json '{}'] [--body-json '{}'] [--plan-out plan.json]`
- Live reads for GET methods (requires credentials; no `--apply` needed):
  - `youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live`
  - Media downloads (methods marked `supportsMediaDownload`, example: captions):
    - `youtube-api-tool api captions.download --params-json '{"id":"CAPTION_TRACK_ID"}' --live --download-to ./captions.vtt`
    - If the output file already exists: add `--download-overwrite` (or global `--yes`).
  - Pagination (GET methods with `nextPageToken`):
    - `youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live --paginate --max-pages 3`
- Writes (non-GET) create plans, and confirmed apply currently requires explicit no-snapshot approval before provider write when no saved snapshot or provider backup is available:
  - `youtube-api-tool --apply --yes api <resource.method> --params-json '{}' [--body-json '{}']`
  - Delete methods also require `--ack-irreversible`.
- Attempt from a reviewed plan file (recommended for risky writes; currently requires explicit no-snapshot approval before provider write when no saved snapshot is available):
  - `youtube-api-tool --apply --yes --plan-in plan.json api <resource.method>`
  - For delete methods: `youtube-api-tool --apply --yes --ack-irreversible --plan-in plan.json api <resource.method>`
  - When using `--plan-in`, do not pass request-building flags (`--params-*`, `--body-*`, `--upload-*`, `--download-*`, `--paginate`, `--max-pages`).
- Upload (mediaUpload methods only; minimum: `videos.insert`):
  - `youtube-api-tool api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4`
  - `youtube-api-tool --apply --yes api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4` (requires explicit no-snapshot approval before upload endpoint use)
  - Resumable uploads:
    - `youtube-api-tool api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4 --upload-protocol resumable`
    - `youtube-api-tool --apply --yes api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4 --upload-protocol resumable` (requires explicit no-snapshot approval before upload session creation)

## Channels (first-class workflows)

Resolve a channel from common inputs (channelId, URL, `@handle`, `/user/<username>`, or plain text). Default is plan-only; pass `--live` to execute official reads:

- Plan-only:
  - `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers`
- Live (official-only reads):
  - `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers --live`
- If multiple candidates are returned (selection required):
  - `youtube-api-tool --output json channels resolve --channel "Some channel name" --live`
  - `youtube-api-tool --output json channels resolve --channel "Some channel name" --live --pick 1`

Export an analysis-ready dataset of ALL public videos for a channel (IDs + watch URLs + metadata/stats). Default is plan-only; pass `--live` to execute:

- Plan-only:
  - `youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export`
- Live export (writes local dataset files under `--out-dir`):
  - `youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export --live`
- If multiple candidates are returned (selection required):
  - `youtube-api-tool --output json channels export --channel "Some channel name" --out-dir ./channel_export --live`
  - `youtube-api-tool --output json channels export --channel "Some channel name" --out-dir ./channel_export --live --pick 1`
- Resume from an interrupted/partial export (progress only, not undo/rollback):
  - `youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export --live --resume`
- `--resume` reads `checkpoint.json` from the same `--out-dir` and continues the export.
  It is progress resume, not a rollback operation.
- Overwrite protection:
  - If `--out-dir` is not empty, pass `--overwrite` (or global `--yes`) or use `--resume`.

## Jobs

- `youtube-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `youtube-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv` (write rows require explicit no-snapshot approval before write/receipt)

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `youtube-api-tool runs list [--limit 20]`
- `youtube-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/refusal workflow examples)

- `youtube-api-tool demo read`
- `youtube-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `youtube-api-tool --apply --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource` (refuses and does not create a receipt)
