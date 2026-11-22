---
name: pinterest-api-safe-cli
description: Read Pinterest boards, pins, analytics, and catalogs. Save and review board and pin changes before applying them.
---

# Pinterest

Use `pinterest-api-tool --output json` to read the account, boards, and pins. Check the signed-in username before working. Follow the [quickstart](docs/quickstart.md), and keep credentials in the local settings file.

Before changing a board or pin, save a preview with `--plan-out` for the signed-in account. Show the exact change for approval. Use the matching file with `--plan-in` and the flags in the [approval guide](docs/safety_model.md). Report what Pinterest shows after the change. If a create result is unclear, check before retrying.
