# TheMealDB test results

## November 23, 2026 local checks

Both fresh CLI installs passed 21 offline tests. From an empty folder I used saved or simulated replies to search for Spicy Arrabiata Penne, open the recipe, and check that an empty search stays valid. An unexpected reply could no longer pass the connection check. With a fake key, I verified that its plain and URL forms stayed out of results, errors, debug output and the optional log.

A fresh local Codex install matched all 47 files under `themealdb-safe-reader`. Before these changes, the published CLI found Spicy Arrabiata Penne and opened its ingredients and instructions through the live V1 API with the development key.

## May 21, 2026 checks

The original checks covered the free TheMealDB V1 reads. Sixteen tests passed. The saved API replies came from TheMealDB using public test key `1`.

### Commands used in the original checks

- `qwayk-themealdb-safe-agent-cli --output json --version`
- `qwayk-themealdb-safe-agent-cli --output json auth check`
- `qwayk-themealdb-safe-agent-cli --output json categories`
- `qwayk-themealdb-safe-agent-cli --output json search name --name Arrabiata`
- `qwayk-themealdb-safe-agent-cli --output json lookup id --meal-id 52772`
- `qwayk-themealdb-safe-agent-cli --output json filter category --category Seafood`

## Saved replies

- [auth check](examples/outputs/auth_check.json)
- [categories](examples/outputs/categories.json)
- [filter area canadian](examples/outputs/filter_area_canadian.json)
- [filter category seafood](examples/outputs/filter_category_seafood.json)
- [filter ingredient chicken breast](examples/outputs/filter_ingredient_chicken_breast.json)
- [list areas](examples/outputs/list_areas.json)
- [list categories](examples/outputs/list_categories.json)
- [list ingredients sample](examples/outputs/list_ingredients_sample.json)
- [lookup 52772](examples/outputs/lookup_52772.json)
- [random](examples/outputs/random.json)
- [search name arrabiata](examples/outputs/search_name_arrabiata.json)
- [version](examples/outputs/version.json)

## Run the tests

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

See the [command guide](command_reference.md) for setup and errors and [API coverage](api_coverage.md) for the 11 reads.
