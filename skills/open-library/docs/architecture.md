# Architecture

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
