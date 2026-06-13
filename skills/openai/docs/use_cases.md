# What you can do with OpenAI

OpenAI is useful when you need an agent to inspect account resources, choose the right API operation, and plan risky actions before anything live or spend-sensitive runs.

Ask the agent for the work a builder or operations person needs before touching production AI resources: model review, file and vector store checks, assistant or thread inspection, usage review, project access checks, batch planning, fine-tune planning, and careful response calls.

## Good questions to ask

- "Which OpenAI operations are available in this tool?"
- "Which models, files, assistants, threads, or vector stores should we review?"
- "Can you check usage, projects, or organization access before we change anything?"
- "Which operation fits this API job?"
- "Can you prepare a plan for this file upload or vector store update?"
- "Can you preview a response call before it spends money?"
- "Can you plan this batch or fine-tune job and save the plan for review?"
- "What approval is needed before this delete-like or spend-money action?"

## Everyday work this helps with

### Account and resource review

The agent can inspect models, files, assistants, threads, vector stores, usage, projects, and organization resources so you know what exists before choosing an operation.

### Operation selection

Ask the agent to list or show the shipped OpenAI operations and explain which one fits the job. This is useful when the API surface is broad and the wrong operation could waste time or money.

### Spend-sensitive planning

For responses, batches, fine-tunes, uploads, deletes, or other write-like actions, the agent should show the operation, target, inputs, cost risk, and approval gates first.

### Reviewable run history

The agent can save plans, receipts, refusals, and run history so a person can check what was planned or applied later.

## What the agent should show you

- The exact operation it plans to use.
- Whether the request is a read, write, delete-like action, or spend-sensitive action.
- The target resource, input payload, and approval gates.
- A review plan before live write-like or spend-money work.
- Any no-snapshot limit before a write goes live.
- Where the saved plan, receipt, refusal, or run history will be.

## Good first path

Start with: "Check the OpenAI skill is configured, list the available operations, and show me the safest live read or review steps before we plan changes."

After that, ask one useful follow-up, such as: "Show me which operation fits this vector store task" or "Preview this response call and explain the spend risk first."
