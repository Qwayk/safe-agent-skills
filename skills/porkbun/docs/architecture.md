# Architecture

This tool is a small single binary with fixed commands and one official source-of-truth inventory.

- `cli.py`: parser, command surface, safe-plan apply flow, and execution guardrails
- `config.py`: `.env` parsing and allowed host selection
- `http.py`: request transport using official base URLs only
- `output.py` and `privacy.py`: output serialization and value-aware secret scrubbing
- `secure_files.py`: owner-only reservation, fsync, and atomic replacement for sensitive local files
- `errors.py`: structured failure handling
- `resources/operation_inventory.json`: generated command map (66 commands)
- `resources/porkbun-openapi-v3.9.json`: pinned OpenAPI snapshot
- `tests/test_cli.py`: behavior and safety tests
- `tests/test_api_inventory.py`: boundary, deterministic-generation, coverage, and packaged-resource tests

Saved plans are authenticated with a local HMAC-SHA-256 key before any plan field is trusted. The public `plan_hash` remains an identifier, not the security boundary.

The requests transport never follows redirects, and the runtime treats every `3xx` response as an error. No command runner, job engine, raw request bridge, custom host, or webhook receiver is part of this tool.
