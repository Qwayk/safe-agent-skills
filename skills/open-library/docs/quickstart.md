# Quickstart

Start with a small Open Library read: checking books, authors, editions, and identifiers with public data.

Need more ideas? See [What you can do with Open Library](use_cases.md). Need setup help? See [Use Open Library with no account](onboarding.md).

A good first ask is:

> Find five books about Dune and show which matches look most useful.

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
pip install -e .
```

## 2. Check setup

Open Library does not need a private account for the first public read. Still run the local check so you know the command works.

```bash
cp .env.example .env
```

```bash
qwayk-open-library-safe-agent-cli --output json --version
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
qwayk-open-library-safe-agent-cli --output json search books --q "harry potter" --limit 3
```

```bash
qwayk-open-library-safe-agent-cli --config local-open-library.json --output json search books --q "poetry"
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Open Library is read-only here and needs no account for the first read. The useful limit is data quality: ask the agent to show the matched edition or author before relying on it.

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
- For setup details, read [Use Open Library with no account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
