# Command reference

Use this page when you need the exact YouTube command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do with YouTube](use_cases.md), [Connect your YouTube account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `youtube-api-tool onboarding [--no-write-env]`

## Auth

- `youtube-api-tool --output json --version`
- `youtube-api-tool auth check`
- `youtube-api-tool auth login --console` (plan/refusal; does not run the OAuth browser/console flow or write token state yet)
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
    - You need a valid caption track ID and the right account access; this is not a general public-caption scraper.
  - Pagination (GET methods with `nextPageToken`):
    - `youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live --paginate --max-pages 3`
- Writes (non-GET) create plans first:
  - `youtube-api-tool api <resource.method> --params-json '{}' [--body-json '{}']`
- Apply a reviewed write when no saved state exists:
  - `youtube-api-tool --apply --yes --ack-no-snapshot api <resource.method> --params-json '{}' [--body-json '{}']`
- Delete methods also require `--ack-irreversible`:
  - `youtube-api-tool --apply --yes --ack-no-snapshot --ack-irreversible api <resource.method> --params-json '{}'`
- Attempt from a reviewed plan file:
  - `youtube-api-tool --apply --yes --ack-no-snapshot --plan-in plan.json api <resource.method>`
  - For delete methods: `youtube-api-tool --apply --yes --ack-no-snapshot --ack-irreversible --plan-in plan.json api <resource.method>`
  - When using `--plan-in`, do not pass request-building flags (`--params-*`, `--body-*`, `--upload-*`, `--download-*`, `--paginate`, `--max-pages`).
- Upload (mediaUpload methods only; minimum: `videos.insert`):
  - `youtube-api-tool api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4`
  - `youtube-api-tool --apply --yes --ack-no-snapshot api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4`
  - Resumable uploads:
    - `youtube-api-tool api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4 --upload-protocol resumable`
    - `youtube-api-tool --apply --yes --ack-no-snapshot api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{...}' --upload-file /path/to/existing-video.mp4 --upload-protocol resumable`

## Channels (first-class workflows)

Resolve a channel from common inputs (channelId, URL, `@handle`, `/user/<username>`, or plain text). Default is plan-only; pass `--live` to execute official reads:

- Plan-only:
  - `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers`
- Live (official-only reads):
  - `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers --live`
- If multiple candidates are returned (selection required):
  - `youtube-api-tool --output json channels resolve --channel "Some channel name" --live`
  - `youtube-api-tool --output json channels resolve --channel "Some channel name" --live --pick 1`

Export an analysis-ready dataset of public videos returned by a channel's uploads playlist (IDs + watch URLs + metadata/stats), subject to YouTube API access, quota, and paging limits. Default is plan-only; pass `--live` to execute:

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
- `youtube-api-tool --apply --yes --ack-no-snapshot --plan-in plan.json jobs run --file jobs.csv` (write rows are planning/refusal examples today; they are not real YouTube writes)

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
- `youtube-api-tool --apply --yes --ack-no-snapshot --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource` (refuses and does not create a receipt)
