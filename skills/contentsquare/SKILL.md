---
name: contentsquare-safe-cli
description: Use Contentsquare to read exports, visitor metrics and Speed Analysis Lab reports, or prepare a reviewed export, enrichment or event change.
---

# Contentsquare

Start with the user's account and project. If setup is missing, run `contentsquare-safe-cli onboarding` and use the connection check it prints. Keep the chosen settings file and project on subsequent commands. Once OAuth works, use a small read the user can recognize, such as `contentsquare-safe-cli data-export list-jobs --limit 5`.

Use the [quickstart](docs/quickstart.md) and [command guide](docs/command_reference.md) for the exact commands. The CLI selects the normal OAuth scope for each API. For account-level credentials, set `CONTENTSQUARE_PROJECT_ID` or pass `--oauth-project-id`. Keep secrets, tokens, and raw authentication replies out of chat.

Use the [approval guide](docs/safety_model.md) before an export job, enrichment batch, or event change. Show the saved preview, wait for approval, and use the required flags. If the tool refuses, explain the reason. If Contentsquare accepts an export job, use the follow-up command to check its runs. If the result is uncertain, check Contentsquare before trying again.

When downloading an export with multiple parts, select a part with `--part-id` or `--file-index`. In your answer, say what you checked, what Contentsquare returned, where you saved any result, and what remains open.
