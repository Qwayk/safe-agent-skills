# Quickstart

If you want task ideas first, start with [What you can do](use_cases.md) and [Connect your account](onboarding.md).

This page is technical. It shows the exact Figma CLI commands.

## 1) Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2) Add your local config

```bash
cp .env.example .env
figma-safe-agent-cli onboarding
```

Edit `.env` with your real values.

If you use OAuth, store the token file locally too:

```bash
figma-safe-agent-cli auth token set --file token.json
figma-safe-agent-cli auth token status
```

## 3) Check auth

```bash
figma-safe-agent-cli auth check
```

## 4) Run safe reads first

```bash
figma-safe-agent-cli operations list --area files
figma-safe-agent-cli operations users get-me
figma-safe-agent-cli operations files get-file-meta --file-key YOUR_FILE_KEY
```

## 5) Preview a write

```bash
figma-safe-agent-cli operations comments post-comment \
  --file-key YOUR_FILE_KEY \
  --body-json-file body.json \
  --plan-out plan.json
```

## 6) Apply only after review

Current Figma writes need explicit no-snapshot approval when no saved before-state is available:

```bash
figma-safe-agent-cli --apply --yes --ack-no-snapshot operations comments post-comment \
  --file-key YOUR_FILE_KEY \
  --body-json-file body.json \
  --plan-in plan.json \
  --receipt-out receipt.json
```

Need machine-readable output? `--output json` is the default.
