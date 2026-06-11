# Use cases

Use this page when you want ideas for real Bluesky jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This file is for non-technical readers.

You can ask an AI agent to do safe batches and changes with review before every write:

- Pull lists and account details for reporting.
- Find and inspect targets before attempting any update.
- Run bulk updates from a CSV with preview first.
- Run real-time subscriptions and review raw frames before acting on them.

What the agent should show you:

1) Dry-run output for every change request first.
2) Read-only checks with `--live` for fresh source data.
3) `--apply` only after explicit approval.
4) An explicit no-snapshot approval and proof paths after write attempts.

Important limits in this tool:
- write attempts require explicit no-snapshot approval before provider HTTP when no saved snapshot is available.
- Subscription output is raw websocket frame data, not fully decoded event objects.
