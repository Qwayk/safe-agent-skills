# Proof and verification

ElevenLabs proof should answer a simple question: what has actually been checked for voices, text-to-speech jobs, history downloads, and account resources, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check voice/account reads, generation plans, and download proof before trusting audio work.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: `Codex`
- Tool version: `0.1.0`
- Provider API version: `ElevenLabs non-legacy public API (as of March 2026)`
- Environment: local offline tests; historical live proof from 2026-03-29 remains documented below

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `elevenlabs-api-tool --output json --version`

3) Auth/config check:
   - `elevenlabs-api-tool --output json --env-file .env.example auth check`
   - To actually validate the key against ElevenLabs, rerun with `--live --out ./auth.json --overwrite` so the CLI writes the sensitive response to disk and stdout only prints the fingerprint.

4) Representative read query:
- `elevenlabs-api-tool --output json --env-file .env.example voices list`
- `elevenlabs-api-tool --output json --env-file .env.example models list`
- `elevenlabs-api-tool --output json --env-file .env.example usage get`
- `elevenlabs-api-tool --output json --env-file .env.example history list`

5) Representative write plan:
- `elevenlabs-api-tool --output json --env-file .env.example tts synthesize --voice-id voice-123 --text "hi" --out ./out.mp3`
- `elevenlabs-api-tool --output json --env-file .env.example --live --apply --ack-spend-money tts synthesize --voice-id voice-123 --text "hi" --out ./out.mp3`
  - Expected current result: explicit no-snapshot approval before API key use or provider HTTP.
- `python3 -m unittest -q tests/test_commands.py` (ensures every CLI command registers and the plan endpoint inventory test passes)

## Live smoke evidence

The following live paths were exercised on 2026-03-29 UTC before the current before-state reset:

- Auth + account read: `auth check --live --out`
- Workspace reads: `voices list`, `models list`, `usage get`, `history list --live --out`
- Audio generation/download: `tts synthesize`, `tts stream`, `history download`
- Upload/media flows: `stt transcribe`, `forced-alignment create`, `voice-changer convert`, `audio-isolation convert`, `dialogue convert`, `sound-effects generate`
- Workspace/ConvAI admin proof: `convai tools create/update/delete`, `workspace webhooks create/delete`

source note:
- Read-only live flows still execute with `--live` and required `--out` flags.
- Write applies now require explicit no-snapshot approval before provider HTTP when no saved snapshot is available. Local proof should expect a refusal only when approval is missing or a true safety blocker is present; approved supported writes emit receipts.

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal output; approved apply emits a receipt that records no-snapshot approval)

## What can go wrong

- **Invalid API key / wrong scopes** → the plan-only `/auth check` outlined above only verifies your local config and never exercises the ElevenLabs service, so it cannot fail. Rerun the live check with `--live --out ./auth.json --overwrite` to capture the real ElevenLabs response; stdout stays file-only, fingerprints only, and the file will show `ok=false` or the precise provider error when the key or scopes are wrong.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** (if the tool supports writes) → verify writes require the normal gates first, then require explicit no-snapshot approval before provider HTTP with `before_state.status: no_snapshot_available` when command-specific before-state capture is not available. Successful write receipts must record the no-snapshot approval and recovery limit.
- **Paid-plan gates** → some endpoints are wired correctly but still return provider plan limits on free workspaces (for example music APIs and voice design). Record these as provider constraints, not CLI failures.
- **Fixture-limited admin flows** → some commands need real workspace fixtures such as service accounts, agent tests, or knowledge-base docs. Mark those separately from broken commands.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`

Latest local verification on 2026-06-04 UTC: `.venv/bin/python -m unittest -q tests.test_commands tests.test_run_artifacts` passed with `34` tests; full-suite result is recorded in the lifecycle note when this pass closes.
