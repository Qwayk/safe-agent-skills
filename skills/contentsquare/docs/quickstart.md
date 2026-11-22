# Quickstart

Check your connection and list a few export jobs from the project you mean to use.

## Check your connection

Install the CLI from the [README](../README.md#install). Run `contentsquare-safe-cli onboarding`, fill your settings as shown in the [setup guide](onboarding.md), and run the connection check it gives you. Use the same settings file and project for the read below. Global flags such as `--env-file` and `--oauth-project-id` go before the command.

## List five export jobs

```bash
contentsquare-safe-cli data-export list-jobs --limit 5
```

Check that the jobs belong to the project you expected. The list can be empty when there are no jobs. A working token and a successful export read tell you this connection can use Data Export. Check other APIs separately when you need them.

If you have Metrics access, you can read a site's bounce rate. Replace the example project ID and dates with your own:

```bash
contentsquare-safe-cli metrics site bounce-rate --project-id 123 --start-date 2026-06-01 --end-date 2026-06-07
```

## Useful next requests

- “Show me which runs finished for this export and whether their files are ready.”
- “Show me the project's visits and conversion rate for last week.”
- “List the segments, goals, page groups, or zones I need for a metrics request.”
- “Open the latest Speed Analysis report for this monitoring ID.”
- “Prepare a plan for this export, enrichment batch, or Speed Analysis event and show it to me before applying.”

Use the [command guide](command_reference.md) for the exact options and the [approval guide](safety_model.md) for changes.
