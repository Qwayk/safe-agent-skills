# Architecture

## Runtime
- `cli.py`: command parsing and dispatch from the local catalog.
- `config.py`: reads `.env`, validates required values, builds API root.
- `registry.py`: loads `src/.openapi/pipedrive_endpoint_catalog.json`.
- `http.py`: HTTP client with redaction-safe logging.
- `output.py`: one-object JSON output contract.
- `errors.py`: shared error types for stable JSON payloads.

## Safety and scope
- No write modules are enabled in runtime.
- No jobs runner, no plan/receipt flow.
- `files download` is implemented as metadata-only metadata check only.
