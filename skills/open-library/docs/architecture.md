# Architecture

Open Library is built as a small command-line tool for public books, authors, editions, subjects, and ISBN data. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Open Library.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Open Library."

## Architecture notes

Simple read-only architecture:

- `cli.py`: command parsing, shared flags, command dispatch.
- `commands.py`: one function per command family.
- `config.py`: merge `.env` + optional `--config` values and validation.
- `api_helpers.py`: shared GET-only request path builder.
- `http.py`: request client with fixed `User-Agent` and timeout.
- `output.py`: deterministic text/JSON output.
- `audit_log.py`: optional JSONL log when `--log-file` is set.
- `errors.py`: validation and predictable error shapes.

No jobs, runs, token store, or write modules are exposed in this release.
