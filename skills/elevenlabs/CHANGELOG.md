# Changelog

## 0.1.0 — current OpenAPI refresh

- Refreshed the pinned official schema to SHA-256 `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`.
- Preserved the 300-path, 388-operation boundary and exposed Twilio answering-machine detection request fields plus the `answering_machine_detection` webhook event in generated contracts.
- Added the two current official multi-context stream-input WebSocket plan commands for text-to-speech and text-to-dialogue.

All notable changes to this project are documented here.

## [Unreleased]

### Changed

- Reconciled customer-facing docs with the pinned ElevenLabs snapshot: 388 HTTP operations, 367 stable implemented commands, and 21 deprecated operations.
- Documented seven manual WebSocket surfaces, including the callback-only speech-engine upstream socket, plus the callback-only Twilio initiation webhook and one docs-only authentication row outside the HTTP count.
- Replaced template batch examples and OAuth-token examples with ElevenLabs-specific placeholders and commands.
- Clarified that local tests and fixtures are deterministic proof only; live provider behavior is unverified.
- Clarified no-snapshot approval and recovery-limit fields in plans and receipts.

### Sources

- `openapi.json` SHA-256: `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`
- Official realtime and Twilio references are listed in [docs/references.md](docs/references.md).

### Package proof (2026-09-03)

- Built wheel and sdist with `python -m build --wheel --sdist`; both archives include the
  generated runtime inventory and contain no `.env`, `.state`, cache, or private-workspace
  paths.
- Fresh-venv installed smoke covered version/help, auth/voices/models/usage plans, one
  generated TTS plan, one sensitive-output plan, and one WSS plan; no provider calls were made.
- `inventory_generator.py` is source-maintenance code; the supported installed CLI uses the
  packaged generated ledger, while regeneration and drift checks run from the source checkout.
- Final generated inventory SHA-256: `53dee1fe15bd9045ba47e633e782ed7444da9f424b8b5a37e6c9d06c0110d824`.
- Final archives: `elevenlabs_api_tool-0.1.0-py3-none-any.whl` (133,785 bytes) and
  `elevenlabs_api_tool-0.1.0.tar.gz` (135,485 bytes).
- Final artifact SHA-256: wheel `0d2b1898fc8301f129cba0af3307b55e9d7d5c9d3c6028cfe60d3fd3b9bb48a7`;
  sdist `aa19f5ace6d0c9c1b4cd6c5ffd6fb1ab601cb757018e46d2e912a47b5868145e`.
- Added the public `GET /v1/convai/triage-tickets` workspace-list command as a sensitive
  read requiring `--out`; no authenticated/live provider call was made.
