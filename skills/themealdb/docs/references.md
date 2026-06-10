# References

These are the sources used to build and check this tool.

## Official sources

- TheMealDB API Guide: `https://www.themealdb.com/docs_api_guide.php`
  - Used for the documented free V1 endpoint list, free vs premium boundaries, V1 auth path format, and the Images section scope decision.
  - Last verified (UTC): `2026-05-21`
- TheMealDB V1 categories endpoint: `https://www.themealdb.com/api/json/v1/1/categories.php`
  - Used to confirm live payload shape for the `categories` command and the read-only `auth check` probe.
  - Last verified (UTC): `2026-05-21`
- TheMealDB V1 list endpoints:
  - `https://www.themealdb.com/api/json/v1/1/list.php?c=list`
  - `https://www.themealdb.com/api/json/v1/1/list.php?a=list`
  - `https://www.themealdb.com/api/json/v1/1/list.php?i=list`
  - Used to confirm the live payload shape for category names, area records, and ingredient records.
  - Last verified (UTC): `2026-05-21`
- TheMealDB V1 filter endpoint example: `https://www.themealdb.com/api/json/v1/1/filter.php?a=Canada`
  - Used to confirm the guide note that area filters accept the documented `Canada` example, not only `Canadian`.
  - Last verified (UTC): `2026-05-21`

## Extra notes

- No third-party guides were used.
- Premium V2 pages and upload features were intentionally excluded from the implementation scope.
