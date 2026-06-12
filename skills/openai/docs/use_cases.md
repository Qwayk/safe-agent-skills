# What you can do with OpenAI

OpenAI work usually starts with choosing the right operation and understanding the risk before a live API call runs.
If you need setup first, start with [Connect your OpenAI access](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

- "Check my OpenAI setup and confirm which live reads are safe to run first."
- "List the available OpenAI operations and help me find the right one for this job."
- "Review models, files, assistants, threads, vector stores, or usage before we change anything."
- "Check project or organization access before we plan a real change."
- "Prepare a careful plan for a file upload, response call, vector store update, or other write."
- "Show me the review steps for a spend-money action before anything goes live."
- "Build a reviewed plan for batch or fine-tune work and save it so I can check it first."

## What the agent should show you

- The exact operation it plans to use.
- Whether the request is only a read, a write, spend-sensitive, or irreversible.
- The live-read or dry-run plan before any API call that matters.
- Any no-snapshot limit before a write goes live.
- Where the saved plan, receipt, or run history will be.

## What it does not promise

- It does not promise a built-in undo path for every OpenAI write.
- It does not treat spend-money actions like cheap or harmless reads.
- It does not guess the right operation or payload when the target is unclear.
