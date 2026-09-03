# ElevenLabs

The ElevenLabs tool helps an agent work with voice and audio: inspect voices and models, generate speech, transcribe recordings, create dubbing or music jobs, and review the account before credits or files are involved.

You can ask your agent to find a suitable voice, check usage, turn a script into an audio file, transcribe a meeting, review a dubbing project, or inspect ElevenAgents conversations and analytics. It can also prepare agent tests, assign a Twilio number for inbound calls, and place an outbound call when those actions are enabled for your account.

For example: “List my voices and models,” “Check usage before we generate this narration,” “Transcribe this recording to a local file,” or “Review yesterday’s ElevenAgents conversations and audio.” For a live action, be specific about the agent, number, file, language, or destination.

The safest first ask is: “Check my ElevenLabs account, list the available voices and models, and stop before generating audio or changing anything.” The agent reads first, explains what it found, and prepares a plan before a live change. Reads need `--live`; writes need `--live --apply`; paid generation and real-world calls need extra approval. Binary or sensitive results stay in files.

## Start here first

- [Try one useful result](docs/quickstart.md)
- [Choose a real ElevenLabs job](docs/use_cases.md)
- [Connect an account](docs/onboarding.md)
- [Understand approvals and limits](docs/safety_model.md)

## What your agent can do

- Voice, model, usage, and speech-history checks.
- Text-to-speech, dialogue, voice changing/design, sound effects, audio isolation, transcription, forced alignment, dubbing, and music workflows.
- ElevenAgents creation and configuration, test creation and runs, knowledge-base work, conversation text/audio/analytics review, and summaries.
- Twilio phone-number assignment and supported inbound/outbound calling workflows.
- Workspace, webhook, and other account administration where your plan and permissions allow it.

## What happens before live changes

The CLI is dry-run by default. The agent should show the exact target, request, output path, spend risk, and recovery limit first. Review the saved plan and mark its `reviewed` field `true`, then use `--live --apply --plan-in <reviewed-plan.json> --receipt-out <receipt.json>`. Generation, transcription, music, voice design, and calls may spend credits; phone calls and other external actions can affect real people. If a before-state cannot be saved, the apply also needs explicit no-snapshot approval. The receipt is written before provider I/O so an uncertain attempt remains durable. Nothing promises automatic rollback.

## What access this tool needs

Set an ElevenLabs API key in `ELEVENLABS_API_KEY`. Some voice, dubbing, music, ElevenAgents, workspace, and telephony features require a paid plan, workspace role, configured integration, or provider-side entitlement. Keep local output paths ready for audio, transcripts, phone data, conversations, and other sensitive results.

## Install and first run

Install slug: `elevenlabs`

```bash
npx skills add Qwayk/safe-agent-skills@elevenlabs -g -y
elevenlabs-api-tool onboarding
elevenlabs-api-tool --output json auth check
```

Then ask the safe first question above. For exact flags and less common command families, use the [command guide](docs/command_reference.md).

## What it covers today

The command inventory is generated from the shipped ElevenLabs API boundary and includes the speech, media, workspace, and ElevenAgents families documented in [API coverage](docs/api_coverage.md). Coverage can still be account-, plan-, fixture-, or live-verification-limited; the coverage and proof pages call those limits out.

## Limits

- No provider call happens without `--live`.
- Live reads and writes can expose sensitive data or spend credits, so `--out` is required for binary and selected sensitive results.
- Live provider behavior is not asserted for every account or endpoint. Local tests are offline; see [proof and verification](docs/proof.md).
- Some telephony, workspace, music, dubbing, and ElevenAgents actions need paid features, roles, configured destinations, or real fixtures.

## Helpful docs

[Docs lobby](docs/README.md) · [Quickstart](docs/quickstart.md) · [Command guide](docs/command_reference.md) · [Authentication](docs/authentication.md) · [API coverage](docs/api_coverage.md) · [Proof](docs/proof.md)
