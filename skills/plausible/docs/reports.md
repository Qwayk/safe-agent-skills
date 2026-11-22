# Plausible reports

Both reports read data and return one JSON result. Check the site, date range, and each section's row count before using the numbers.

## Weekly traffic report

This gives you top pages, traffic channels, and the goals Plausible returns for the selected period. Use the separate membership command below if you also want membership counts.

```bash
plausible-api-tool --env-file .env report weekly --days 7 --limit 50
```

To save the tables as CSV files, pass an output directory:

```bash
plausible-api-tool --env-file .env report weekly --days 7 --limit 50 --out-dir ./reports
```

Each table shows whether its results are complete and the next offset when more rows may exist. CSV files contain the rows returned for those tables. Check the JSON before treating a CSV as a full export.

## Membership report

```bash
plausible-api-tool --env-file .env report membership --days 30 --limit 50
```

This report uses named signup and membership goals. Check `missing_goals` when using it on a new site. An unconfigured goal has an unavailable count. A configured goal with no events shows zero. If a step is unavailable, the report leaves its comparison blank. The counts are separate totals per step. They do not establish how many of the same people moved through those steps.

Use `--out-dir` for a report run or pass `--config <file.json>` with `reports_out_dir` as a project default. Keep the list of goals your site uses in its project. For repeat reports, use the named commands with the site, date range and metrics visible.
