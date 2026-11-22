---
name: bluesky-safe-cli
description: Read Bluesky profiles and feeds, and review account changes before sending them.
---

Use `bluesky-safe-cli` for Bluesky API requests. Start with the [quickstart](docs/quickstart.md) for a public feed or a reviewed post. Use the [command reference](docs/command_reference.md) to find other operations.

1. Read public profiles and feeds with `--live`. Sign in explicitly with `auth login` for private data and changes. Use `auth check` to confirm the account.
2. For a change, preview the request. Show the server, account, fields and recovery limits, and get approval. `--live --apply` sends an approved write. Include `--ack-no-snapshot` when the preview says there is no saved copy of the previous state. Follow the preview for any `--yes` or `--ack-irreversible` flags.
3. To create or update a post, save the preview with `--plan-out` and apply it with `--plan-in` and the same request. If anything changes, preview it and ask again. Read the post back using the receipt's URI and compare the content ID and text. Check whether the post already exists before retrying an unclear result.

Use JSON output and report the result or refusal. Keep settings, tokens and private records out of chat. [Safety guide](docs/safety_model.md)
