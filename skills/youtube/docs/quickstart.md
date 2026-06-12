# Quickstart

Want the short non-technical path first? Start with [What you can do with YouTube](use_cases.md), [Connect your YouTube account](onboarding.md), and [How this skill stays safe](safety_model.md).

This technical command path is for local developer/test setup, safe first reads, channel export, and your first careful write plan.

If you installed the public skill through your agent host, you usually do not need the Python setup below. Use it when you are working from a local checkout of this tool or when you want to run the test suite yourself.

Requires: **Python 3.12+**.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy the example env file to `.env`, then fill what you need:

```bash
cp examples/example.env .env
```

In a source checkout that also includes `.env.example`, this works too:

```bash
cp .env.example .env
```

- `YOUTUBE_API_KEY=...` for many public reads
- `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json` for OAuth work

If you already have a valid token JSON from a separate approved flow, keep it at `.state/token.json` next to your `.env`.

Tip: for a guided first-time setup, run:

```bash
youtube-api-tool onboarding
```

Important: `auth login` and `auth token set` still stop at the plan/refusal step today, so they do not write the token file automatically yet.

## 3. First safe checks

Version check with no `.env` required:

```bash
youtube-api-tool --output json --version
```

Pinned discovery inventory with no network:

```bash
youtube-api-tool methods list
```

Local auth/config check:

```bash
youtube-api-tool auth check
```

If you want to inspect the current OAuth helper behavior:

```bash
youtube-api-tool auth login --console
```

## 4. First live reads

Plan a read first:

```bash
youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}'
```

Then run the real GET call only when you mean it:

```bash
youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live
```

Resolve a channel safely:

```bash
youtube-api-tool --output json channels resolve --channel @GoogleDevelopers
youtube-api-tool --output json channels resolve --channel @GoogleDevelopers --live
```

## 5. First channel export

Plan the export first:

```bash
youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export
```

Run the local export only when you mean to create the files:

```bash
youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export --live
```

If the folder already has files, use `--resume` or approve an overwrite.

## 6. First careful write plan

Preview a write without sending it yet:

```bash
youtube-api-tool api playlists.insert --params-json '{"part":"snippet,status"}' --body-json '{"snippet":{"title":"Example playlist"},"status":{"privacyStatus":"private"}}'
```

Preview an upload without uploading bytes:

```bash
youtube-api-tool api videos.insert --params-json '{"part":"snippet,status"}' --body-json '{"snippet":{"title":"Example video"},"status":{"privacyStatus":"private"}}' --upload-file /absolute/path/to/existing-video.mp4
```

The upload file must exist because the plan records its path, size, and modified time. Do not run the apply version until you have reviewed the plan and really intend to upload or change YouTube.

When a reviewed write or upload has no saved state to restore from, the apply shape is:

```bash
youtube-api-tool --apply --yes --ack-no-snapshot api <resource.method> ...
```

Delete methods also need `--ack-irreversible`.

For a download flow, plan or run a caption download to a real file path. You need a valid caption track ID and the right account access; the official API does not allow downloading captions for every public video.

```bash
youtube-api-tool api captions.download --params-json '{"id":"CAPTION_TRACK_ID"}' --live --download-to ./captions.vtt
```
