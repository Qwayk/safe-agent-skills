---
name: elevenlabs-safe-cli
description: Use the ElevenLabs CLI for voice, audio, speech, dubbing, music, ElevenAgents, conversations, analytics, and calling with plan-first approvals.
---

Use this skill when the user asks an agent to inspect or change ElevenLabs content, account resources, ElevenAgents, conversations, analytics, or phone integrations.

1. Resolve the concrete voice, model, file, agent, conversation, language, number, or destination. Refuse to guess.
2. Use `--output json` and run an explicit command from `docs/command_reference.md` without `--live` to produce a plan. For current reads, add `--live`; sensitive reads also need `--out <path>`.
3. Show the plan’s target, request, spend/external-action risk, `before_state`, recovery contract, and verification. Do not apply until the user explicitly approves.
4. For approved writes, use `--live --apply`; add `--ack-no-snapshot` when no before-state is available. Add `--ack-spend-money` for generation, transcription, music, voice design/changing, isolation, alignment, and other paid media work.
5. Treat Twilio assignment, inbound/outbound calls, batch calls, deletes, and sensitive conversation work as higher risk. Require the command’s extra confirmations and a clearly approved destination.
6. Keep audio, transcripts, phone numbers, conversations, webhook data, and other binary or sensitive results file-only with `--out`. Never print secrets or payloads.

Useful first ask:

```text
Check my ElevenLabs account, list the available voices and models, and stop before generating audio or changing anything.
```

The CLI has no network behavior without `--live`, but paid plans, roles, fixtures, and provider availability can still limit a live request. Check `docs/api_coverage.md` and `docs/proof.md`; do not promise automatic rollback or universal live support.
