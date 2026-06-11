# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

> **Plan-first workflow**: read-only commands execute once you add `--live`. Write/spend-sensitive calls still require `--live --apply` plus the needed acknowledgements, and write applies require explicit no-snapshot approval before provider HTTP when command-specific before-state capture is not available.

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
elevenlabs-api-tool onboarding
```

3) Smoke test

```bash
elevenlabs-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
elevenlabs-api-tool --output json --version
```

If you want to run the template without creating a real `.env` yet, you can point at `.env.example`:

```bash
elevenlabs-api-tool --env-file .env.example auth check
```

4) Explore the core workflows (still plan-only by default):
- `elevenlabs-api-tool --output json voices list`
- `elevenlabs-api-tool --output json models list`
- `elevenlabs-api-tool --output json usage get`
- `elevenlabs-api-tool --output json history list`
- `elevenlabs-api-tool --output json tts synthesize --voice-id <voice> --text \"hello\" --out ./out.mp3`

Add `--live` when you are ready to actually read data. Generation and admin writes still require `--live --apply` plus the safety acknowledgements, `--out`, and `--plan-in` checks documented in `docs/safety_model.md`, then require explicit no-snapshot approval before provider HTTP when no saved snapshot is available.

5) Live-tested starter path

These read flows were rechecked against the live ElevenLabs API on 2026-03-29 UTC:

- `elevenlabs-api-tool --output json --live auth check --out ./auth.json`
- `elevenlabs-api-tool --output json --live voices list`
- `elevenlabs-api-tool --output json --live models list`
- `elevenlabs-api-tool --output json --live usage get`
- `elevenlabs-api-tool --output json --live history list --out ./history.json`
- `elevenlabs-api-tool --output json --live --apply --ack-spend-money tts synthesize --voice-id <voice> --model-id eleven_multilingual_v2 --text "hello" --out ./out.mp3`
  - Expected approved result: provider apply runs only after explicit no-snapshot approval and the receipt records the recovery limit.
- `elevenlabs-api-tool --output json --live --apply history download --history-item-id <id> --out ./history.mp3`
  - Expected approved result: provider apply runs only after explicit no-snapshot approval and the receipt records the recovery limit.
- `elevenlabs-api-tool --output json --live --apply --ack-spend-money stt transcribe --body '{"model_id":"scribe_v1"}' --file audio=@./sample.mp3 --out ./transcript.json`
  - Expected approved result: provider apply runs only after explicit no-snapshot approval and the receipt records the recovery limit.

Notes:
- `usage get` uses a default recent time window for live calls. Add `--start-unix` and `--end-unix` to override it.
- File-upload endpoints use `--file key=@path`. For example, STT/audio isolation/voice changer use `audio=@./sample.mp3`.
- Music and voice-design endpoints may still return paid-plan errors on free accounts even when the CLI wiring is correct.
