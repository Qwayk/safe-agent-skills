# Architecture

TheMealDB is built as a small command-line tool for public meals, ingredients, categories, areas, and recipe lookups. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches TheMealDB.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for TheMealDB."

## Architecture notes

The code path is intentionally small:

1. `cli.py` parses global flags and named commands.
2. `config.py` loads safe defaults, `.env`, and optional JSON config.
3. `http.py` makes the request and redacts custom keys from error text.
4. `commands/auth.py` runs the read-only health check.
5. `commands/meals.py` maps each free V1 endpoint to one explicit command.

## Design choices

- No generic request command
- No write workflow
- One command per covered endpoint or endpoint family
- Output normalized enough to be easy to use, but still close to the API payload shape
