# Skill wrapper guidance

Use the ElevenLabs skill when the user wants an agent to inspect or change ElevenLabs voices, audio, speech, dubbing, music, ElevenAgents, workspace resources, or telephony. Use it for a concrete service job—generating narration, transcribing a file, reviewing conversations, testing an agent, assigning a number, or checking analytics—not for arbitrary shell or raw HTTP requests.

## Operating loop

1. Resolve the concrete voice, model, file, agent, conversation, language, number, or destination; refuse to guess.
2. Run plan-only. Reads need `--live` only when current provider data is requested.
3. Present the plan, including spend, external-call risk, `before_state`, recovery, and verification.
4. Wait for explicit approval before `--live --apply`; add `--ack-no-snapshot` when no before-state can be saved.
5. Add `--ack-spend-money` for paid media or generation and command-specific confirmations for deletes, batches, or calls.
6. Save binary or sensitive responses with `--out`; report only path, size, and fingerprint.

Always use `--output json` for structured results. Never request or print API keys, headers, `.env` contents, webhook secrets, phone data, transcripts, conversation content, or audio payloads.

## Safe first commands

```bash
elevenlabs-api-tool --output json auth check
elevenlabs-api-tool --output json voices list
elevenlabs-api-tool --output json models list
elevenlabs-api-tool --output json usage get
```

These are local plan checks unless `--live` is added. A live auth check or sensitive inventory must include `--out <path>`.

Apply writes a durable pending receipt before provider I/O. Output files are verified locally; eligible exact-path PUT/PATCH writes perform status-only paired GET readback and report reachability, not field-level equality. Unsupported verification remains explicit.

## Stop conditions

Stop and ask when a target is ambiguous, credentials or permissions are missing, a paid feature is unavailable, the request could call a real person, or the runtime cannot enforce the plan/review/apply loop. Do not imply that every endpoint will work live: consult [API coverage](api_coverage.md) and [proof](proof.md) for account and fixture limits.
