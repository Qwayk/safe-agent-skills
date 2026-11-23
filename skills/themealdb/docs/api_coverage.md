# TheMealDB API coverage

The table lists the 11 public V1 recipe reads in this tool. The original endpoint review was on May 21, 2026. The standard API address is `https://www.themealdb.com/api/json/v1`. The examples below use test key `1` for development and education. [TheMealDB API guide](https://www.themealdb.com/api.php)

`auth check` reads `categories.php` to verify the connection. `onboarding` shows local setup help. Neither adds a recipe endpoint.

| Endpoint | Capability | CLI command | Status | Safety | Tests and examples | Notes |
|---|---|---|---|---|---|---|
| `GET /1/search.php?s={meal_name}` | Search meals by full name | `search name --name <meal_name>` | implemented | read-only | `tests/test_meals_commands.py`, `docs/examples/outputs/search_name_arrabiata.json` | The API returns a `meals` list or `null` for no matches. The CLI reports no matches as an empty list. |
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

## Other TheMealDB features

The random selection, latest recipes, multiple-ingredient filters and uploads are outside this tool's public reads. Image-size URLs return images and are outside this JSON command list. Consult the [provider docs and terms](references.md) for access rules. [Test results](proof.md)
