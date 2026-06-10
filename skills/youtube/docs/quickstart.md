# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
youtube-api-tool onboarding
```

3) Smoke test

```bash
youtube-api-tool auth check
```

OAuth login planning (currently requires explicit no-snapshot approval before token writing):

```bash
youtube-api-tool auth login --console
```

If you want a safe machine-readable version output (no `.env` required):

```bash
youtube-api-tool --output json --version
```

If you want to inspect the pinned YouTube method inventory (no `.env` required):

```bash
youtube-api-tool methods list
```

Dry-run a method call (deterministic plan; no network):

```bash
youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}'
```

Live read (GET only; requires credentials):

```bash
youtube-api-tool api search.list --params-json '{"part":"snippet","q":"cats","maxResults":5}' --live
```

Resolve a channel (plan-only by default; official-only reads require `--live`):

```bash
youtube-api-tool --output json channels resolve --channel @GoogleDevelopers
youtube-api-tool --output json channels resolve --channel @GoogleDevelopers --live
```

Export a channel videos dataset (plan-only by default; local files are written only with `--live`):

```bash
youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export
youtube-api-tool --output json channels export --channel @GoogleDevelopers --out-dir ./channel_export --live
```

Media download (supportsMediaDownload methods, example: captions):

```bash
youtube-api-tool api captions.download --params-json '{"id":"CAPTION_TRACK_ID"}' --live --download-to ./captions.vtt
```
