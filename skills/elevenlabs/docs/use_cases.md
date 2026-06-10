# Use cases

Use this page when you want ideas for real ElevenLabs jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with voice and media work

ElevenLabs work often means checking voices, planning spend-sensitive generation, and keeping large audio outputs out of chat until you are ready:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run → explicit apply gates → missing-approval refusal when no saved snapshot is available)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/logs) you can keep for proof and debugging

## Common use cases (examples)

- “Check whether my ElevenLabs key is working before I try anything expensive.”
- “List my voices and available models so I can pick the right one.”
- “Review my recent generation history and then see the exact missing-approval refusal for downloading one audio file when no saved snapshot is available.”
- “Draft a text-to-speech generation first, then tell me what approval is needed if no saved snapshot is available.”
- “Check current usage before I launch more audio generation.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Try live apply only after explicit confirmation and required safety flags.
3) For writes, show the explicit no-snapshot approval instead of pretending the write happened.
4) Point to the saved plan, refusal, and proof artifacts.
