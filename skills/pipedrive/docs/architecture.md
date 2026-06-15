# Architecture

Pipedrive is built as a small command-line tool for CRM deals, leads, activities, people, organizations, products, and pipelines. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Pipedrive.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Pipedrive."

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
