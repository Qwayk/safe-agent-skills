# Proof and verification

Use this page when you want the clearest proof story for TikTok Marketing.

This repo does not rely on live TikTok ad accounts for normal proof. The evidence here comes from the local suite, the pinned official manifest, the committed redacted examples, and the explicit live-gating and no-snapshot behavior.

## What is already proved

- The pinned TikTok Marketing operation surface loads and registers correctly.
- The tool exposes `240` named operations from the pinned official manifest.
- `auth check` works as the dedicated live credential helper.
- Dry-run plans, multipart planning, refusal behavior, and run history are covered locally.
- Current write-like operations still require explicit no-snapshot approval when real saved before-state is missing.

## Last checked

- Local docs and contract alignment rechecked: **2026-06-11 UTC**
- Local suite and proof baseline: **2026-06-04 UTC**
- Tool version: `0.1.0`
- Provider surface: pinned manifest `official_operations_v1_2026-05-24.json`

No live TikTok credentials are stored here, so this proof pack stays local-first and redacted on purpose.

## Core validation

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest -q
.venv/bin/tiktok-marketing-api-tool --output json --version
.venv/bin/tiktok-marketing-api-tool --output json api ops list
```

## Committed examples

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

The current `receipt.example.json` is still a missing-approval refusal example, not a claim that the current write-like operations already have rollback support.

## What can still go wrong

- wrong app credentials
- expired or missing token
- missing advertiser permissions
- wrong request JSON shape for a specific operation
- write-like operations that still have no real saved before-state

## How to verify the risky parts

- If auth fails, check app credentials, token source, and advertiser access first.
- If a read plan looks wrong, inspect the pinned operation and the query or body JSON before using `--live`.
- If a write-like operation refuses, confirm it stopped before provider HTTP.
- If a future approved write path succeeds, confirm the proof output records the no-snapshot approval and recovery limit.

## Intentional limits

Not covered on purpose:

- generic rollback claims for current write-like operations
- hidden live reads through the broad `api` surface
- fake proof of live advertiser access when real credentials are missing
