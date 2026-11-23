# TheMealDB commands

Follow the [quickstart](quickstart.md) to install the tool. Put global options before the command, for example `qwayk-themealdb-safe-agent-cli --output json search name --name "Arrabiata"`.

## Recipe reads

Add one of these commands after `qwayk-themealdb-safe-agent-cli`.

```text
search name --name <meal-name>
search first-letter --letter <letter>
lookup id --meal-id <id>
random
categories
list categories
list areas
list ingredients
filter ingredient --ingredient <name>
filter category --category <name>
filter area --area <name>
```

Use the names returned by the list commands. For example, `filter ingredient --ingredient chicken_breast` shows matching meals. Open a meal by ID for the ingredients, measures and directions. `list ingredients` returns the full ingredient list, so use it when you need to find or compare ingredient names.

## Optional settings

TheMealDB provides test key `1` for development and education. The tool uses it by default with `https://www.themealdb.com/api/json/v1` and a 30-second timeout. An app-store release using the API requires paid access. If you already have a supporter key, set `THEMEALDB_API_KEY` in a local `.env` file or your shell. Keep the key out of chat and shared files. The tool still uses the 11 recipe reads above. [TheMealDB API access](https://www.themealdb.com/api.php) · [Terms of use](https://www.themealdb.com/terms_of_use.php)

- `--env-file <PATH>` selects a local settings file. The default is `.env`.
- `--config <PATH>` reads non-secret JSON defaults, `base_url` and `timeout_s`.
- `THEMEALDB_BASE_URL` and `THEMEALDB_TIMEOUT_S` can be set in the shell or settings file. Shell settings take priority over the file, then JSON defaults and then built-in defaults. `--timeout-s <SECONDS>` sets the wait for one run and takes priority over saved values.
- `onboarding --no-write-env` shows settings help. `onboarding` can create a local file with the development defaults.
- `auth check` reads meal categories to check the connection and shows whether the tool is using the public key or a custom key.

## Output and errors

- `--output json|text` chooses the format. JSON is the default.
- `--version` shows the installed version.
- `--verbose` shows request details on standard error. `--debug` shows an error trace. `--log-file <PATH>` saves a local log as one JSON object per line.
- If a search is empty, check the spelling or try a different title. For a filter, check the exact value from the matching list command.
- If a reply is unexpected or access fails, read the error. If you're using your own key, check it in your local settings and try the connection check.
