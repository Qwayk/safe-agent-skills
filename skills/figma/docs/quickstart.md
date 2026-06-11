# Quickstart (technical)

This is the technical setup page with commands.
If you want plain-English setup and task ideas, start with `use_cases.md` and `onboarding.md`.

## 1) Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2) Add your config

```bash
cp .env.example .env
```

Edit `.env` with your real values.
For onboarding flow, run:

```bash
figma-safe-agent-cli onboarding
```

## 3) Verify connection

```bash
figma-safe-agent-cli auth check
```

If you use OAuth, first store the token file:

```bash
figma-safe-agent-cli auth token set --file token.json
figma-safe-agent-cli auth token status
```

## 4) Run a safe read

```bash
figma-safe-agent-cli operations list --area files
figma-safe-agent-cli operations files get-file --file-key YOUR_FILE_KEY
```

## 5) Preview a write and see the safe refusal

```bash
figma-safe-agent-cli operations comments post-comment \
  --file-key YOUR_FILE_KEY \
  --body-json-file body.json
```

This is dry-run output only. Apply only after review; current source will require explicit no-snapshot approval before Figma token use or provider HTTP when no saved snapshot is available:

```bash
figma-safe-agent-cli --apply --yes operations comments post-comment \
  --file-key YOUR_FILE_KEY \
  --body-json-file body.json
```

Need structured output? Use `--output json` (default).
