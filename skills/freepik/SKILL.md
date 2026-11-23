---
name: freepik-api-safe-cli
description: Search Freepik stock photos, show previews, and download approved assets with freepik-api-tool.
---

# Freepik

Use the documented `freepik-api-tool --output json` commands for provider work. For API key setup, see [Connect your account](docs/onboarding.md). Keep account keys in a private env file.

1. Search and show previews first. Use `search photos --query "QUERY" --exclude-ai --shortlist`, then `resource get --id ID` and `preview --id ID`. With `--exclude-ai`, only assets with both non-AI flags set to false are shown. When the user asks you to choose, pick within their requirements and prepare that asset for review.
2. Save a preview using `--plan-out` as shown in the [quickstart](docs/quickstart.md). Show the exact account, asset IDs, format or size, destination and any repeat download or overwrite. Explain that the license can use credits and the tool cannot undo it.
3. After the user approves, use the same request with `--plan-in`, `--apply` and `--ack-no-snapshot`. Add `--yes` for a batch. If any approved setting changes, save and review a new preview.
4. Report the saved files, license links, available download IDs and inventory rows. If a request stops or its outcome is unclear, follow the [download error guide](docs/safety_model.md#when-a-download-stops) before making another license request.

`--write-jobs` and `preview --save-preview` save local review files. Use [the command reference](docs/command_reference.md) for all options.
