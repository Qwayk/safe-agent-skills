# Query recipes

Use a query file when you want to choose the exact site, period, filters and metrics. Plausible reads the query at `POST /api/v2/query`.

Notes:
- Pagination in Stats API v2 is set via the `pagination` object, not a top-level `limit`.
- `stats validate` checks the JSON locally without an API key. A live query checks whether Plausible accepts it.

Keep any site-specific event/goal catalog in your project folder (not inside this tool repo).

## List goals (top conversions)

```bash
python3 -m plausible_api_tool --env-file .env stats goals list --date-range 30d --limit 50
```

Or with a raw query file:

```bash
python3 -m plausible_api_tool --env-file .env stats query --file examples/goals_list_query.json
```

## Validate a query JSON file

```bash
plausible-api-tool stats validate --file examples/goals_list_query.json
```

## Break down a goal by a custom property

Example: `members_modal_shown_manual` by `placement`:

```bash
python3 -m plausible_api_tool --env-file .env stats goals breakdown \\
  --goal "members_modal_shown_manual" \\
  --prop placement \\
  --date-range 30d
```

## Timeseries for a goal (daily)

```bash
python3 -m plausible_api_tool --env-file .env stats goals timeseries \\
  --goal "member_gate_cta_click" \\
  --date-range 30d
```

## Top pages by pageviews (raw query example)

This uses a visit/session metric, so it is safe to group by page dimensions.

```bash
python3 -m plausible_api_tool --env-file .env stats query --query '{
  "site_id": "example.com",
  "date_range": "30d",
  "metrics": ["pageviews", "visitors"],
  "dimensions": ["event:page"],
  "order_by": [["pageviews", "desc"]],
  "pagination": {"limit": 50, "offset": 0}
}'
```
