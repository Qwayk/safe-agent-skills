# ElevenLabs

Install slug: `elevenlabs`

Use this skill when you want your AI agent to review voices, history, workspace settings, or generation tasks in ElevenLabs with clearer preview before live work.

The tool covers the non-legacy ElevenLabs API surface with explicit commands. Reads stay plan-first until you opt into live work, spend-sensitive actions need extra approval, and binary or sensitive outputs stay file-based instead of dropping raw payloads into chat.

## For non-technical users: start here

- [What you can do](docs/use_cases.md)
- [Connect your account](docs/onboarding.md)
- [How live generation stays safer](docs/safety_model.md)

## What is already covered

- Voices, models, history, workspace/admin, ConvAI, webhooks, dubbing, audio isolation, forced alignment, and other non-legacy API areas all map to explicit CLI commands.
- Live generation, transcription, music, and similar spend-sensitive paths need `--live --apply --ack-spend-money`.
- When a write cannot save real before-state, approved apply also needs explicit no-snapshot approval before ElevenLabs HTTP.

## Proof and limits

- Core live workflows were revalidated on 2026-03-29 UTC. See [Proof pack](docs/proof.md) for the exact live-checked commands.
- Some endpoints still need a paid ElevenLabs plan or customer-side fixtures, so the docs call those limits out honestly in [API coverage](docs/api_coverage.md) and [Proof pack](docs/proof.md).

## For technical users: start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof pack](docs/proof.md)
- [Docs index](docs/README.md)

## Testing

Run the unit suite from the tool root:

```
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

Every command emits exactly one JSON object on stdout, even on validation errors, and the suite is offline-only (no live ElevenLabs calls).
The local suite remains offline-only, but the tool now also has documented live smoke coverage in `docs/proof.md`.
