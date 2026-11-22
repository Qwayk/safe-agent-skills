---
name: threads-safe-cli
description: Read Threads profiles, posts and replies, and review new posts before publishing.
---

Use the documented `threads-api-tool` commands for Threads API requests. Start with `auth check` to confirm the account and `posts list-owned` to read recent posts. See the [quickstart](docs/quickstart.md) and [command reference](docs/command_reference.md) for examples.

Preview every change. Show the user the account, text, attachments, and action before asking for approval. Use `--apply --ack-no-snapshot` for an approved change without a saved copy of the previous state. Deletes also need `--yes --ack-irreversible`.

Save a plan with `--plan-out` before creating or publishing a post. Apply it with `--plan-in` and the matching request. After publishing, check whether the receipt confirms the separate post read. If the outcome is unclear, check the draft status or read the post before trying again.

Keep settings, secrets and tokens private. The [coverage list](docs/api_coverage.md) describes Web Intents and webhook setup for people working outside the CLI.
