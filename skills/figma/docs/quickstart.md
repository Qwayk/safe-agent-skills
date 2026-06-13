# Quickstart

This technical quickstart helps you get one useful Figma result quickly, without turning the page into a full command manual.

If you are still deciding what to ask, start with [What you can do with Figma](use_cases.md). If setup is not done yet, read [Connect your account](onboarding.md).

A good first ask is:

> Check that Figma is connected, run one safe read, and tell me what I should look at first.

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
cp .env.example .env
figma-safe-agent-cli onboarding
```

```bash
figma-safe-agent-cli auth check
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
figma-safe-agent-cli operations list --area files
figma-safe-agent-cli operations users get-me
figma-safe-agent-cli operations files get-file-meta --file-key YOUR_FILE_KEY
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

## What good output looks like

A useful first result should tell you:

- what account, workspace, project, page, item, or public data was checked
- whether the tool connected successfully
- what the first read returned
- what the result means in normal language
- what is safe to do next
- where the plan, receipt, export, or saved file lives if the command created one

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
