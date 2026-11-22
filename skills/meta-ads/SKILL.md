---
name: meta-ads-api-safe-cli
description: Read Meta Ads accounts, campaign results, and creatives, and export reports with the Meta Ads CLI.
---

# Meta Ads

Start with the account the user chose. If you need to find it, use the saved settings or list the accounts the token can read.

```bash
meta-ads-api-tool --output json ad-accounts list --fields id,name
```

Use the documented CLI commands for Meta requests. If the tool is missing, use the Quickstart in the tool folder to install it. Keep tokens in local settings or the shell.

For a report, give the account, dates, metrics, and any breakdowns. Use the same settings for both periods. If pages, rows, or fields are missing, explain the gap before drawing conclusions. Check `manifest.json` for a snapshot and share the path to the saved files. Download assets when the user asks for them.

Use this tool for reads and local exports. The [command guide](docs/command_reference.md) and [snapshot guide](docs/snapshot_export.md) show the available work.
