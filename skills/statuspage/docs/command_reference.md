# Statuspage commands

Use the public page root with `--base-url`, or [save a default page](onboarding.md). Put shared flags before the command.

| Command | What it shows |
| --- | --- |
| `statuspage-api-tool summary get` | Overall status, open incidents, planned or active maintenance, and components when the page lists them. Start here for a current check. |
| `statuspage-api-tool status get` | Overall status only. |
| `statuspage-api-tool incidents list` | Up to 50 recent incidents, including resolved incidents. |
| `statuspage-api-tool maintenances list` | Up to 50 recent scheduled maintenance records, including completed maintenance. |
| `statuspage-api-tool auth check` | Whether the tool needs credentials. This runs locally. |
| `statuspage-api-tool --help` | Commands and flags. |
| `statuspage-api-tool --output json --version` | Installed version. |

For repeated checks, run the same command for each page URL. Keep the results separate by page.

The default output is JSON. Use `--output text` for a readable printout or `--log-file` for local JSONL command events. See the [saved outputs](examples/README.md) and [output rules](safety_model.md).
