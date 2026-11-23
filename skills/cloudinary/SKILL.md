---
name: cloudinary
description: Find Cloudinary images and videos, read their settings, and show a preview before sending an approved change.
---

Use `cloudinary-safe-agent-cli --output json`. Start with [Quickstart](docs/quickstart.md) and [Connect Cloudinary](docs/onboarding.md). Keep Cloudinary secrets out of chat.

Find the exact library, asset, folder, or account resource first. Use `operations list` or `operations show` to find its named command. Media reads use media credentials. Account commands use the separate account connection.

For a write, save and show the preview with `--plan-out`. Ask for approval of the exact target, inputs, and recovery limit. Apply with `--plan-in`, `--apply --yes`, and the required acknowledgements. Signed uploads protect existing media by default. See [Approve and check changes](docs/safety_model.md) for replacements, deletes, access-key changes, and proceeding without a saved copy of the previous state.

Save private or binary results with `--out` inside `--project-dir`. Tell the user whether the tool stopped, Cloudinary replied, or a follow-up confirmed the change. Give the receipt path. Check Cloudinary before retrying a write with an unclear result.
