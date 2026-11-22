---
name: instagram-safe-cli
description: Read posts and comments from an Instagram professional account and review changes before sending them.
---

Use `instagram-api-tool` for Instagram API requests and prefer JSON output. Start with `auth check` to confirm the professional account, then `media list` to see recent posts. The [quickstart](docs/quickstart.md) walks through the first read and a reviewed post.

Preview any change and show the target and exact request before asking for approval. Use `--apply --ack-no-snapshot` for approved changes without a saved copy of the previous state. Publishing, sending a message and deleting a comment also need `--yes`. Deleting a comment needs `--ack-irreversible`.

Use `--plan-out` before creating a draft or publishing it and `--plan-in` with the same request when applying. Check the receipt and the result of the separate post read. If the reply is unclear, check the draft status before trying again. [Review and check changes](docs/safety_model.md)

Keep access tokens, app secrets and sign-in codes private. This tool uses Instagram Login for professional accounts. Refer to [API coverage](docs/api_coverage.md) for features outside that scope, including Business Discovery and Hashtag Search.
