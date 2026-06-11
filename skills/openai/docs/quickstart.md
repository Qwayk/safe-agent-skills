# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your OpenAI access](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill your OpenAI values.

If you want the tool to create the starter file for you, run:

```bash
openai-api-tool onboarding
```

## 3. Local smoke checks

Version output with no network call:

```bash
openai-api-tool --output json --version
```

List the pinned operation catalog locally:

```bash
openai-api-tool api ops list
```

## 4. First live check

Real network reads still require `--live`:

```bash
openai-api-tool --output json --live auth check
```

## 5. First safe live reads

List models:

```bash
openai-api-tool --live api listModels
```

Review one model:

```bash
openai-api-tool --live api retrieveModel --path model=gpt-4.1-mini
```

## 6. Plan a write-capable action

Write-capable operations start as dry-run plans by default, so save the plan first:

```bash
openai-api-tool --plan-out plan.json api createResponse --body-json '{"model":"gpt-4.1-mini","input":"Hello"}'
```

Nothing goes live in this step.

## 7. Request apply only after review

After you review `plan.json`, spend-money actions can need all of these gates:

```bash
openai-api-tool --live --apply --plan-in plan.json --yes --ack-spend-money --ack-no-snapshot api createResponse --body-json '{"model":"gpt-4.1-mini","input":"Hello"}'
```

Delete-like actions can also require `--ack-irreversible`.

## 8. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [API coverage](api_coverage.md)
