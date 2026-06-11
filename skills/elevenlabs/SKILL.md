---
name: elevenlabs-safe-cli
description: Run `elevenlabs-api-tool` safely (dry-run first, explicit commands, binary/spend gates).
---

This page is the agent-facing rule sheet for the public ElevenLabs skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safety wrapper for Qwayk’s ElevenLabs CLI.

Core rules (do not break):
- Always run `--output json` so the wrapper can parse one JSON object.
- Never print or request secrets (API keys, `xi-api-key` headers, `.env` contents, OTPs).
- All commands default to plan-only. Do not add `--live` until the user approves a plan.
- Generation/music/spend commands must add `--ack-spend-money` before the tool is allowed to live-apply.
- Binary or sensitive responses (media, transcripts, phone numbers, webhooks) require `--out <path>` and never emit the payload in stdout.
- Check `plan.before_state` and `plan.recovery`; current write plans must show `before_state.status: no_snapshot_available` when no snapshot can be saved.
- Irreversible/destructive writes also require `--yes` plus `--plan-in` when replaying a saved plan; confirm the plan fingerprint matches.
- The tool now exposes every non-legacy ElevenLabs endpoint; use `docs/api_coverage.md` for the inventory and required gates. Current write applies need required approval before ElevenLabs API key use or provider HTTP when no before-state can be saved.

Safe workflow (offline):
1) Validate configuration: `elevenlabs-api-tool --output json auth check`.
2) Pick an explicit command from `docs/command_reference.md`, verify required selectors/flags, and run without `--live` to inspect the generated plan JSON.
   - For workspace metadata: start with `voices list` or `history list`.
3) Share the plan with the user; only after explicit approval give them the `--live --apply --ack-no-snapshot` command when no snapshot can be saved, expecting a receipt for supported approved writes or an exact tool limitation when no executor exists.
4) For generation outputs, add `--ack-spend-money --out ./out/<name>.<ext>` and confirm `--overwrite` / `--yes` approvals before rerunning.
5) For current binary writes/downloads, report the approval gate or exact limitation; read-only live outputs still report `file_path`, `size_bytes`, and `sha256` instead of raw payloads.

References:
- `docs/safety_model.md`
- `docs/command_reference.md`
- Agent skill prompt and install notes are included with this package.
