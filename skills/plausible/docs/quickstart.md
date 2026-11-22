# Run your first Plausible query

Start with one site and seven days of traffic. Check the site and period in the reply before using the numbers.

From the tool folder, install the CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
plausible-api-tool --version
```

Follow [Onboarding](onboarding.md) to create your settings file and choose the right Stats API key. Then check the connection and read visits and pageviews:

```bash
plausible-api-tool --env-file .env auth check
plausible-api-tool --env-file .env stats query --query '{"date_range":"7d","metrics":["visits","pageviews"]}'
```

The result lists metric values in the same order as the query. Look at Plausible's returned query for the actual site and period it used. For top pages and traffic sources, run a [weekly report](reports.md). For a local JSON check before connecting, see [query recipes](queries.md#validate-a-query-json-file).
