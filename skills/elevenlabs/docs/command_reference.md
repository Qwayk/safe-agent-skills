# Command reference

Use this page when you need the exact ElevenLabs command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `elevenlabs-api-tool onboarding [--no-write-env]`
- Dry-run write plans now include `no_snapshot_available` before_state metadata plus a `recovery` contract. write applies require explicit no-snapshot approval when no saved snapshot exists; approved applies must emit receipts that record the recovery limit.

## Auth

- `elevenlabs-api-tool --output json --version`
- `elevenlabs-api-tool auth check`
  - Dry-run plan by default. Add `--live --out <file>` (and `--overwrite` when reusing the path) to capture the real JSON response while stdout only prints the file fingerprint.

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `elevenlabs-api-tool runs list [--limit 20]`
- `elevenlabs-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Voices

- `elevenlabs-api-tool voices list`
  - Dry-run plan by default.
  - Add `--live` to actually fetch the workspace voices; verification is manual (inspect the list in JSON).

## Models

- `elevenlabs-api-tool models list`
  - Dry-run plan by default.
  - Add `--live` to fetch the current ElevenLabs model catalog.

## Usage

- `elevenlabs-api-tool usage get`
  - Dry-run plan by default.
  - Add `--live` to fetch current usage and quota metadata for the workspace.

## Text-to-speech (TTS)

- `elevenlabs-api-tool tts synthesize --voice-id <voice> --text "<message>" --out <file>`
  - Plan-only default; the plan lists the HTTP request + payload.
  - Apply still requires `--live --apply --ack-spend-money --out <file>`.
  - Expected result: missing no-snapshot approval refuses before ElevenLabs API key use or provider HTTP; approved apply records the recovery limit.
  - `--plan-in <plan.json>` enforces drift detection before the explicit no-snapshot approval.

## Speech history

- `elevenlabs-api-tool history list [--limit N]`
  - Lists history entries; the plan shows the query metadata.
  - Use `--live --out <file>` (with `--overwrite` for repeated runs) to store the live JSON securely; the CLI will only emit the file fingerprint on stdout.
- `elevenlabs-api-tool history download --history-item-id <id> --out <file>`
  - Plan-only default and requires `--out <file>`.
  - Apply requires `--live --apply` and requires explicit no-snapshot approval before ElevenLabs API key use or provider HTTP because before-state capture is not implemented yet.

## Speech + media operations

- Every non-legacy speech, music, audio, and dialogue endpoint is exposed via `elevenlabs-api-tool <command>` (e.g., `tts stream`, `stt transcribe`, `music compose`, `voice-design create`, `dialogue convert`, `audio-isolation convert`, `dubbing create`, `forced-alignment create`, etc.). The full list lives in `docs/api_coverage.md`.
- These commands accept body input via `--body '{\"prompt\":\"...\"}'`, optional field overrides via `--param key=value`, and respect the same dry-run → gated refusal workflow as the core commands. Plan-first writes require `--live --apply`, binary outputs demand `--out <path>`, and spend-sensitive endpoints need `--ack-spend-money`; after those gates, writes require explicit no-snapshot approval before provider HTTP until before-state capture exists. `stt realtime` runs over WebSocket and is always plan-only; any `--live` or `--apply` attempts are refused, so it never emits an `--out` file.
- Additional explicit media commands:
  - `elevenlabs-api-tool music stream --body '{"prompt":"..."}' --out <file>`
  - `elevenlabs-api-tool music plan create --body '{"prompt":"..."}'`
  - `elevenlabs-api-tool music upload --file audio=@./sample.mp3 --out <file>`
  - `elevenlabs-api-tool music stem-separation --body '{"audio_url":"..."}' --out <file>`
  - `elevenlabs-api-tool voice-changer convert --voice-id <voice> --out <file>`
  - `elevenlabs-api-tool voice-design design --out <file>`
  - `elevenlabs-api-tool voice-design remix --voice-id <voice> --out <file>`
  - `elevenlabs-api-tool voice-design stream --generated-voice-id <id> --out <file>`
  - `elevenlabs-api-tool sound-effects generate --out <file>`
  - `elevenlabs-api-tool dubbing similar-voices --body '{"name":"..."}'`
  - `elevenlabs-api-tool pronunciation-dictionaries list`
  - `elevenlabs-api-tool audio-native create --out <file>`
  - `elevenlabs-api-tool audio-native settings get --project-id <id>`

## Workspace + ConvAI + admin

- Workspace-focused commands (`tokens single-use create`, `service-accounts list`, `workspace resources share`, `workspace webhooks create`, etc.) plus ConvAI helpers (`convai agents list`, `convai knowledge-base get-content`, `convai whatsapp outbound-call`, ...) are also listed in `docs/api_coverage.md`.
- All workspace/ConvAI commands follow the same plan-first workflow: read-only commands execute when you add `--live`, while write-capable commands gate via `--live --apply`, require `--ack-spend-money` for spendy calls, enforce `--out` for sensitive JSON recordings like webhook secrets or phone numbers, and require explicit no-snapshot approval before provider HTTP until before-state capture exists.
- Additional explicit admin commands:
  - `elevenlabs-api-tool service-accounts api-keys list --service-account-user-id <id>`
  - `elevenlabs-api-tool service-accounts api-keys create --service-account-user-id <id> --out <file>`
  - `elevenlabs-api-tool service-accounts api-keys delete --service-account-user-id <id> --api-key-id <id>`
  - `elevenlabs-api-tool workspace invites add --email <email>`
  - `elevenlabs-api-tool workspace groups search --param name=<text>`
  - `elevenlabs-api-tool workspace webhooks list --out <file>`
  - `elevenlabs-api-tool workspace webhooks delete --webhook-id <id> --out <file>`
- Additional explicit ConvAI commands:
  - `elevenlabs-api-tool convai tools list`
  - `elevenlabs-api-tool convai tools create`
  - `elevenlabs-api-tool convai tools update --tool-id <id>`
  - `elevenlabs-api-tool convai tools delete --tool-id <id>`
  - `elevenlabs-api-tool convai knowledge-base list`
  - `elevenlabs-api-tool convai conversations list --out <file>`
  - `elevenlabs-api-tool convai conversations text-search --param text_query=<text> --out <file>`
  - `elevenlabs-api-tool convai tests list`
  - `elevenlabs-api-tool convai tests invocations list --param agent_id=<id>`
  - `elevenlabs-api-tool convai analytics live-count`
  - `elevenlabs-api-tool convai phone-numbers list --out <file>`
  - `elevenlabs-api-tool convai twilio register-call`
  - `elevenlabs-api-tool convai batch-calling submit`
  - `elevenlabs-api-tool convai mcp-servers list`
  - `elevenlabs-api-tool convai llm-usage calculate`
