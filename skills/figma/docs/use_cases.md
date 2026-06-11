# Use cases

Use this page when you want ideas for real Figma jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Discovery and targeting use case

“I want to see which part of our Figma setup this account can safely inspect before we change anything.”

An agent can start with read-only discovery, check which API areas are available for your token,
and narrow the list to the files, teams, or libraries that are safe to inspect first.
This reduces guessing and helps you avoid trying enterprise-only or team-gated endpoints too early.

## Safe write use case

“I want to draft a comment for one file, review it, and only post it after I approve the exact request.”

The tool can prepare a dry-run preview that shows the exact request, the target file,
and the approval gates that must be passed before anything is written.
After review, supported writes can proceed with explicit `--ack-no-snapshot` approval when no saved snapshot is available.

## Access and plan-gate use case

“Tell me which endpoints this workspace can use now, and which ones are blocked by plan, team, or enterprise rules.”

This is useful before you promise work to a customer or start a larger automation.
The tool keeps the documented surface explicit, so it is easy to separate what is locally ready,
what needs live credentials, and what depends on Figma plan or organization rules.

## Audit and traceability use case

“Show me what we already tried, what changed, and where the proof files are.”

The tool keeps local run history, saved plans, receipts or refusal records, and redacted JSON outputs.
That makes it easier to explain results to a customer or review the exact request before repeating it.

## Why this beats typical no-code automation

- It previews writes before applying them, and when no saved snapshot is available it asks for explicit no-snapshot approval instead of guessing.
- It keeps the provider surface explicit instead of hiding behavior behind a generic request bridge.
- It returns deterministic JSON output that is easy to review or reuse.
- It keeps local proof files so you can show what was tested without screenshots.
