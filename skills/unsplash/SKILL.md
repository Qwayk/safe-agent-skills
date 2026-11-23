---
name: unsplash-api-safe-cli
description: Search Unsplash photos, compare collections and photographers, and save approved photos with unsplash-api-tool.
---

# Unsplash

Use documented `unsplash-api-tool --output json` commands for provider work. Keep the Access Key in a private local file or environment variable. Use [the setup guide](docs/onboarding.md) when the connection is missing. Confirm the intended local paths before creating setup files, importing a key, or exporting results.

1. Start with a search and show photo IDs, preview links, and photographer credits. Use the image links Unsplash returns for displays. For links to Unsplash and the photographer, follow the provider's credit guidance in [Unsplash references](docs/references.md). When the user delegates the choice, select within the stated requirements and prepare a preview.
2. Save a download preview with `--plan-out` as shown in the [quickstart](docs/quickstart.md). Show the photo, connection, destination, and any replacement. Explain that Unsplash records the download and the tool cannot undo it.
3. After approval, apply the matching preview with `--plan-in`, `--apply` and `--ack-no-snapshot`. A replacement also needs the reviewed `--overwrite` choice and `--yes`. If the request changes, save and review a new preview.
4. Report whether Unsplash recorded the download and whether the file was saved. Follow the [download error guide](docs/safety_model.md#check-the-result) before repeating a request with an unclear result.
