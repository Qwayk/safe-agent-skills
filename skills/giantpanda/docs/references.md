# References

The [GiantPanda Parking API docs](https://account.giantpanda.com/docs/client-api/) require a GiantPanda sign-in. The August 11, 2026 review used the Authentication, Add Domain(s), and Domain Statistics sections.

- `GET /api/v1/domains/stats/` takes a start date, an end date, and optional paging values.
- `POST /api/v1/domains/add/` takes a list of domain names. The documented HTTP 200 reply lists the names created and already present, with a count for each list.

[Supported commands](api_coverage.md)
