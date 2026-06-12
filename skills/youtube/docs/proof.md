# Proof and verification

Use this page when you want the shortest honest answer to one question: what has really been proved for this YouTube skill so far?

You do not need to run these commands yourself. They are here so you or your agent can audit what ran, what came back, and what still depends on local auth, scopes, or approvals.

Keep the proof safe:
- Never include secrets.
- Use obvious redactions or placeholders in examples.
- Keep this file short, factual, and easy to verify.

## Last verified

Date (UTC): 2026-06-12
Verified by: Codex human-docs workflow test
Tool version: 0.1.0
Provider API: YouTube Data API v3 pinned discovery snapshot
Base URL (default): https://www.googleapis.com
Latest local verification: `65` source unit tests passed, `65` public mirror unit tests passed, and the saved proof examples were refreshed from offline version, auth check, method inventory, search-list plan, channel-resolve plan, channel-export plan, upload-plan, and captions-download plan commands.

Verification commands:
- In the source tool folder: `.venv/bin/python -m unittest -q`
- In the public mirror folder, using an installed Python environment for this tool: `python -m unittest -q`
- Expected output for both folders: `Ran 65 tests` and `OK`
- Saved example outputs are under `docs/examples/` in each folder.

## Smoke checks

Run inside the tool folder:

1. Create venv and install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2. Version check with no `.env` required:
- `youtube-api-tool --output json --version`

3. Pinned method inventory:
- `youtube-api-tool methods list`

4. Local auth/config check:
- `youtube-api-tool --output json auth check`

5. Plan a representative read (no network):
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}'`

6. Plan channel resolution:
- `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers`

7. Plan channel export:
- `youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export`

8. Plan an upload without uploading bytes:
- `youtube-api-tool --output json api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{"snippet":{"title":"Example"},"status":{"privacyStatus":"private"}}' --upload-file /path/to/existing-video.mp4`

9. Plan a caption download path. You need a valid caption track ID and the right access:
- `youtube-api-tool --output json api captions.download --params-json '{"id":"CAPTION_TRACK_ID"}' --download-to ./captions.vtt`

Optional live reads when credentials are ready:
- `youtube-api-tool --output json api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live`
- `youtube-api-tool --output json channels resolve --channel @GoogleDevelopers --live`

## Example outputs (redacted)

These files are committed:
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

## What can go wrong (and how we verify)

- **Wrong auth mode** -> API key is not enough for many private or write-capable actions; verify by checking `auth check` plus one representative live GET read.
- **OAuth helper expectation mismatch** -> `auth login` and `auth token set` still stop at plan/refusal today; verify by checking the refusal output and confirming no `.state/token.json` write happened.
- **Ambiguous channel target** -> `channels resolve --live` can return multiple candidates and require `--pick`; verify by checking the returned candidates before export or write planning.
- **Non-empty export folder** -> `channels export --live` refuses unsafe local output reuse unless you choose `--overwrite`, `--yes`, or `--resume`.
- **Write safety drift** -> verify uploads and non-GET writes still start as plans, and confirm the approval gates stay explicit before risky actions.

## Links

- Sources used: `docs/references.md`
- Coverage details: `docs/api_coverage.md`
