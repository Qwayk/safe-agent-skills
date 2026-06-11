# Proof pack (publish-ready evidence)

Purpose:
- Provide small, verifiable evidence of behavior (offline where possible).
- Point to committed redacted outputs and the pinned discovery snapshot.
- Write apply requires explicit no-snapshot approval before provider writes, uploads, token writes, demo/job writes, or success receipts when before-state/provider-backup support is not available.
- Recovery is explicit in plans/refusals; this tool does not create recoverability mechanisms (no backups/snapshots/provider restore).

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Keep examples deterministic and reviewable.

## Last verified (UTC)

- Date (UTC): 2026-06-04
- Verified by: Codex
- Tool version: 0.1.0
- Provider API: YouTube Data API v3 (pinned discovery snapshot)
- Base URL (default): https://www.googleapis.com
- Latest local verification: `54` unit tests passed, compile check passed, version/example JSON checks passed, and write apply refusal smokes passed.

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version:
- `youtube-api-tool --output json --version`

3) Pinned discovery inventory:
- `youtube-api-tool methods list`

4) Local auth/config check:
- `youtube-api-tool --output json auth check`

5) Plan a method call (no network):
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}'`

6) Plan channel resolution (no network):
- `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers`

7) Plan channel export (no network):
- `youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export`

8) Plan an upload call (no network; never embeds bytes):
- `youtube-api-tool --output json api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{"snippet":{"title":"Example"},"status":{"privacyStatus":"private"}}' --upload-file ./video.mp4`

9) Confirm a write/upload apply requires the right safety gate before provider access:
- `youtube-api-tool --output json --apply --yes api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{"snippet":{"title":"Example"},"status":{"privacyStatus":"private"}}' --upload-file ./video.mp4`

10) Plan a media download call (no network; shows how downloads are saved to a file on live runs):
- `youtube-api-tool --output json api captions.download --params-json '{"id":"CAPTION_TRACK_ID"}' --download-to ./captions.vtt`

Optional (requires credentials; executes live reads):
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live`
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live --paginate --max-pages 2`

## Committed redacted example outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/methods_list.json`
- `docs/examples/outputs/api_call_search_list_plan.json`
- `docs/examples/outputs/channels_resolve_handle_plan.json`
- `docs/examples/outputs/channels_resolve_query_live_refusal.json`
- `docs/examples/outputs/channels_export_plan.json`
- `docs/examples/outputs/api_call_videos_insert_upload_plan.json`
- `docs/examples/outputs/api_call_captions_download_plan.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## Pinned inventory artifacts

- `docs/official_discovery_youtube_v3_rest.json`
- `docs/official_methods.txt`

## Links

- Sources: `docs/references.md`
- Coverage ledger: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
