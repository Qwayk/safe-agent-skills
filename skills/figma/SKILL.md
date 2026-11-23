---
name: figma-safe-cli
description: Read Figma files, comments, and libraries, get image links, and show a preview before sending approved changes.
---

Start with [Quickstart](docs/quickstart.md) and [Connect Figma](docs/onboarding.md). Use `figma-safe-agent-cli --output json`. Keep tokens and private files out of chat.

Start with the file or team the user named. Use `operations list` and `operations show AREA COMMAND` to find the right command. With a limited token, try the read needed for the job. The profile check uses a separate permission. Report which frames rendered when the user asks for images.

Before a write, save the preview with `--plan-out` and show the exact target, change, and recovery limit. Wait for approval. Apply with the saved `--plan-in`, the same Figma connection, and `--apply --yes`. Add `--ack-no-snapshot` once the user approves going ahead without a copy of the previous state. Add `--ack-irreversible` when the command requires it. See [Approve and check changes](docs/safety_model.md).

Report whether the tool stopped, Figma accepted the change, or a follow-up read confirmed it. Share where the receipt was saved. Check the current Figma state before retrying a write with an unclear result.
