# Quickstart

Start with a small Pipedrive read: checking deals, pipelines, people, organizations, and activity data before you build a sales report.

Need more ideas? See [What you can do with Pipedrive](use_cases.md). Need setup help? See [Connect your Pipedrive account](onboarding.md).

A good first ask is:

> Show open deals in this pipeline and group them by stage.

## What you will do first

1. Make sure the local tool can run.
2. Check the account, token, or public access the tool needs.
3. Run one small read and make sure the result matches the real service.
4. Review any local file path before saving exports or reports.

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
```

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli onboarding
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env --output json users get-current
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Pipedrive is read-only here. Your first run should not change CRM data; only review any local export path before saving files.

## What a useful first result includes

A good first result should make these things clear:

- what was checked
- whether the connection worked
- what came back from the service
- what the result means in plain English
- what is safe to inspect next
- where any saved file, export, plan, or receipt was written

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your Pipedrive account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
