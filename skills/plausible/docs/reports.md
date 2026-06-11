# Reports

Reports are “batteries included” read-only commands that run multiple Stats API queries and return **one JSON object**.

## Weekly report

```bash
python3 -m plausible_api_tool --env-file .env report weekly --days 7 --limit 50
```

Optional CSV export:

```bash
python3 -m plausible_api_tool --env-file .env report weekly \\
  --days 7 \\
  --limit 50 \\
  --out-dir <PROJECT_DIR>/plausible-analytics/reports
```

## Membership report

```bash
python3 -m plausible_api_tool --env-file .env report membership --days 30 --limit 50
```

## Notes

- Reports assume you’ve configured the relevant goals in Plausible (Site → Goals).
- Keep any site-specific event/goal catalog in your project folder (not inside this tool repo).
- Reports are safe: they do not mutate Plausible data.
