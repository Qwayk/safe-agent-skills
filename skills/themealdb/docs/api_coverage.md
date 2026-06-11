# API coverage

This file is the main reference for the free TheMealDB V1 read surface this tool covers.

## Summary

- Provider: TheMealDB
- Scope: documented free V1 public read endpoints only
- API base URL: `https://www.themealdb.com/api/json/v1`
- Auth method: V1 API key in the URL path, with public development key `1` used by default
- Last audited (UTC): `2026-05-21`

## Command surface

- `qwayk-themealdb-safe-agent-cli onboarding`
- `qwayk-themealdb-safe-agent-cli auth check`
- `qwayk-themealdb-safe-agent-cli categories`
- `qwayk-themealdb-safe-agent-cli list categories`
- `qwayk-themealdb-safe-agent-cli list areas`
- `qwayk-themealdb-safe-agent-cli list ingredients`
- `qwayk-themealdb-safe-agent-cli search name --name <meal_name>`
- `qwayk-themealdb-safe-agent-cli search first-letter --letter <letter>`
- `qwayk-themealdb-safe-agent-cli lookup id --meal-id <meal_id>`
- `qwayk-themealdb-safe-agent-cli random`
- `qwayk-themealdb-safe-agent-cli filter ingredient --ingredient <ingredient>`
- `qwayk-themealdb-safe-agent-cli filter category --category <category>`
- `qwayk-themealdb-safe-agent-cli filter area --area <area>`

`auth check` is a tool utility command. It uses `categories.php` as a read-only probe, but it is not counted as a separate provider capability.

## Covered free V1 endpoints

| Endpoint | Capability | CLI command | Status | Safety | Tests and examples | Notes |
|---|---|---|---|---|---|---|
| `GET /1/search.php?s={meal_name}` | Search meals by full name | `search name --name <meal_name>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/search_name_arrabiata.json` | Returns `meals` or `null` from the API. CLI normalizes missing results to an empty list. |
| `GET /1/search.php?f={first_letter}` | Search meals by first letter | `search first-letter --letter <letter>` | implemented | read-only | `tests/test_meals_commands.py` | Letter must be one character. |
| `GET /1/lookup.php?i={meal_id}` | Lookup full meal details by ID | `lookup id --meal-id <meal_id>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/lookup_52772.json` | Full recipe payload. |
| `GET /1/random.php` | Fetch one random meal | `random` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/random.json` | Random result shape matches `lookup` and `search`. |
| `GET /1/categories.php` | List full category records | `categories` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/categories.json` | Returns `categories`, not `meals`. |
| `GET /1/list.php?c=list` | List category names | `list categories` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/list_categories.json` | API uses `meals` as the top-level key. |
| `GET /1/list.php?a=list` | List areas | `list areas` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/list_areas.json` | Live payload includes both `strArea` and `strCountry`. |
| `GET /1/list.php?i=list` | List ingredients | `list ingredients` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/list_ingredients_sample.json` | Large payload. |
| `GET /1/filter.php?i={ingredient}` | Filter meals by one ingredient | `filter ingredient --ingredient <ingredient>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/filter_ingredient_chicken_breast.json` | Free V1 supports one ingredient only. |
| `GET /1/filter.php?c={category}` | Filter meals by category | `filter category --category <category>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/filter_category_seafood.json` | Category values come from `list categories`. |
| `GET /1/filter.php?a={area}` | Filter meals by area | `filter area --area <area>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/filter_area_canadian.json` | The guide shows both `Canada` and `Canadian`. Live API accepts both. |

## Out of scope by design

- `GET /v2/1/randomselection.php` — premium V2 only — not planned
- `GET /v2/1/latest.php` — premium V2 only — not planned
- `GET /v2/1/filter.php?i=ingredient1,ingredient2,...` — premium V2 only — not planned
- Upload features and supporter-only features — out of scope — not planned
- Image URL variants under the guide’s Images section — not JSON API endpoints — not planned
