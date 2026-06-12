# ElevenLabs

**Capability:** Reads + careful changes

ElevenLabs is where voice, speech, dubbing, transcription, audio isolation, music, history, and workspace settings can affect real credits, files, and customer-facing audio.

This skill helps an agent check voices and models, review generation history and usage, inspect workspace settings, and prepare audio or admin work before anything spends credits or writes to the account.

Use it for questions like: "Which voices and models can I use?", "What did we generate recently?", "How close are we to usage limits?", "Can you draft this text-to-speech job first?", or "Can you save the live output to a file instead of chat?"

Live ElevenLabs work is careful by default. Reads need `--live`, spend-sensitive generation needs extra approval, and binary or sensitive results stay file-based instead of being dumped into the conversation.

A good first ask is: "Check the ElevenLabs connection, list my voices and models, show current usage, and stop before any generation or downloads."

## Start here first

- Want ideas for real ElevenLabs work? [What you can do with ElevenLabs](docs/use_cases.md)
- Need setup? [Connect your ElevenLabs account](docs/onboarding.md)
- Want the safety story first? [How generation stays safer](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review voices, models, usage, generation history, workspace/admin settings, ConvAI, webhooks, dubbing, and related API areas.
- Prepare text-to-speech, transcription, music, voice design, audio isolation, forced alignment, and similar spend-sensitive work as plans first.
- Save audio, transcripts, history downloads, phone numbers, ConvAI content, webhook secrets, and other sensitive results to local files.
- Check paid-plan or fixture-limited flows without pretending every endpoint is available to every account.
- Keep local proof for plans, refusals, receipts, and live smoke coverage.

## What access this skill needs

- An ElevenLabs API key in `ELEVENLABS_API_KEY`.
- `ELEVENLABS_API_BASE_URL=https://api.elevenlabs.io` unless your environment needs a different official base URL.
- A paid plan or account feature when the ElevenLabs endpoint requires it.
- Local output paths for binary or sensitive live results.

## Install and first run

Install slug: `elevenlabs`

Ask your agent to install the `elevenlabs` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@elevenlabs -g -y
```

Then try a safe first ask like:

```text
Check the ElevenLabs connection, list my voices and models, show current usage, and stop before any generation or downloads.
```

## How this skill stays safe

- No network calls happen without `--live`.
- Writes need `--live --apply`.
- Spend-sensitive generation, transcription, music, voice design, audio isolation, forced alignment, and similar work also need `--ack-spend-money`.
- Spend-sensitive or irreversible operations may need `--ack-irreversible` where the API coverage file says so.
- When a write cannot save real before-state, apply requires explicit no-snapshot approval before ElevenLabs API key use or provider HTTP.
- Binary or sensitive live results must go to `--out`.

## What it covers today

This skill covers the non-legacy ElevenLabs API surface with explicit commands, including:

- voices, models, usage, history, text-to-speech, speech-to-text, dubbing, audio isolation, music, and forced alignment
- workspace/admin, ConvAI, webhooks, phone-number-adjacent content, and other non-legacy API areas
- live smoke coverage for the starter paths documented in the proof pack

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the voice, model, file path, spend risk, and recovery limit.
- Live reads need `--live`.
- Live generation or write apply needs the required approval gates.
- When no before-state can be saved, live apply also needs explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved.
- Supported approved applies can leave receipts that record recovery limits.
- Local run history can include plans, refusals, receipts, and audit logs.
- The proof pack names the live-checked starter commands and the endpoints that still need paid-plan or customer fixtures.

## Limits

- Some ElevenLabs endpoints require a paid plan, real account data, or customer-side fixtures.
- Live output can include audio, transcripts, phone numbers, ConvAI content, or webhook secrets, so those results stay file-only.
- The local test suite is offline-only; live coverage is documented separately in the proof pack.
- The tool does not promise automatic rollback or snapshots for every write path.

## Helpful docs

- [Browse all ElevenLabs docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
