# Quickstart

Get one safe Gemini result first: list the models your key can see, then count or send a small prompt only after the setup check passes.

## 1. Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## 2. Add Your Key Locally

```bash
cp .env.example .env
```

Edit `.env` and set:

```dotenv
GEMINI_API_KEY=replace-with-your-local-key
```

Do not paste the key into chat.

## 3. Check Local Auth Setup

```bash
gemini-api-tool --output json auth check
```

This confirms the key is present without printing it.

## 4. List Models

```bash
gemini-api-tool --output json models list
```

## 5. Try a Small Prompt

```bash
gemini-api-tool --output json models generate-content \
  --model models/gemini-3.5-flash \
  --request-json '{"contents":[{"parts":[{"text":"Explain safe API tools in one sentence."}]}]}'
```

If you need to change Gemini state, start with a plan. For example:

```bash
gemini-api-tool --plan-out plan.json cached-contents delete \
  --name cachedContents/example \
  --ack-no-snapshot
```

Review the plan before any apply command.
