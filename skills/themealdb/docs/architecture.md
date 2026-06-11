# Architecture

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
