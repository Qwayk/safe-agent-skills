# Quickstart

Your first useful result is a local account check followed by a voice, model, or usage inventory. These steps stay plan-only unless you add `--live`, so you can confirm the command and account before generating audio or spending credits.

## 1. Install and configure

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
elevenlabs-api-tool onboarding
```

Put the real key in the local `.env` as `ELEVENLABS_API_KEY`; never paste it into chat.

## 2. Check setup

```bash
elevenlabs-api-tool --output json auth check
```

This is local-only without `--live`. To check the real account, keep the sensitive response in a file:

```bash
elevenlabs-api-tool --output json --live auth check --out ./auth.json
```

Add `--overwrite` only when deliberately replacing that file.

## 3. Read before you create

```bash
elevenlabs-api-tool --output json voices list
elevenlabs-api-tool --output json models list
elevenlabs-api-tool --output json usage get
```

Add `--live` for current provider data. For sensitive history, use `--out`:

```bash
elevenlabs-api-tool --output json --live history list --out ./history.json
```

## 4. Prepare one audio job

This makes a dry-run plan and does not contact ElevenLabs:

```bash
elevenlabs-api-tool --output json tts synthesize --voice-id <voice-id> --text "A short test sentence." --out ./narration.mp3
```

Review the target, text, output path, spend warning, and recovery limit. Save that reviewed plan, then only after explicit approval present a gated apply using `--live --apply --plan-in <reviewed-plan.json> --receipt-out <receipt.json> --ack-spend-money --ack-no-snapshot`. The pending receipt is durable before provider I/O.

## 5. Continue with a real job

Ask: “Transcribe `./meeting.mp3` to `./meeting.json`,” “Create a dry-run plan for an ElevenAgent test,” or “Review my recent conversations and analytics.” The agent should choose an explicit command, use `--out` for sensitive results, and stop for approval before spend or real-world actions.

See the [command reference](command_reference.md) for command-specific flags.
