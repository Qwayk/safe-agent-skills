# Use cases

Use this page when you want ideas for real OpenAI jobs to hand to your agent.
If you need setup first, start with [Connect your OpenAI access](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Common use cases

- "Check my OpenAI setup and confirm which live reads are safe to run first."
- "List the available OpenAI operations and help me find the right one for this job."
- "Review models, files, assistants, threads, vector stores, or usage before we change anything."
- "Check project or organization access before we plan a real change."
- "Prepare a careful plan for a file upload, response call, vector store update, or other write."
- "Show me the review steps for a spend-money action before anything goes live."
- "Build a reviewed plan for batch or fine-tune work and save it so I can check it first."

## Why this skill is more useful than raw docs

This skill gives your agent a safer path through real OpenAI API work.

- It can start with local operation discovery before any live network call.
- It can keep all live reads behind `--live` so nothing reaches the API by accident.
- It can show a dry-run plan before risky, spend-money, or irreversible actions.
- It can leave plans, receipts, run history, docs, and tests in one place so you can inspect what happened.
- It can record when a write needed explicit no-snapshot approval because there was no useful saved before-state.

## What this skill intentionally does not promise

- It does not promise a built-in undo path for every OpenAI write.
- It does not treat spend-money actions like cheap or harmless reads.
- It does not guess the right operation or payload when the target is unclear.
