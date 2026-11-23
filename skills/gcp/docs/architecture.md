# Architecture

The CLI builds its commands from Google’s official API sources. One runtime checks inputs and access, previews changes, checks approval before a write, and records Google’s reply.

## Runtime

The packaged inventory is `src/gcp_safe_agent_cli/gcp_discovery_inventory.json`. That file records the included services, generated operations, path templates, safety classes, risk labels, and official source evidence.

`src/gcp_safe_agent_cli/generated_registry.py` loads that inventory for the runtime. `src/gcp_safe_agent_cli/generated_runtime.py` turns each row into an explicit `service operation` command, validates the input JSON, builds the Google request, checks and saves plans for approval, and records receipts.

The command shape is always:

```bash
qwayk-gcp-safe-agent-cli <service> <operation> --input-json input.json
```

Use the listed operations and their documented inputs.

## Main files

- `scripts/generate_gcp_discovery_inventory.py`: rebuilds the official-source inventory and coverage docs.
- `src/gcp_safe_agent_cli/gcp_discovery_inventory.json`: generated source boundary used by the runtime.
- `docs/api_coverage.md`: human-readable coverage ledger and command lookup table.
- `src/gcp_safe_agent_cli/cli.py`: global flags, built-in commands, and generated service registration.
- `src/gcp_safe_agent_cli/generated_registry.py`: packaged service and operation registry.
- `src/gcp_safe_agent_cli/generated_runtime.py`: generated command execution, plan/apply checks, request construction, and receipt shape.
- `src/gcp_safe_agent_cli/google_auth.py`: Google Application Default Credentials and quota-project handling.
- `src/gcp_safe_agent_cli/project_config.py` loads optional project defaults and resolves file paths. The settings lists in `config.py` and checks in `generated_runtime.py` control which Google Cloud targets the tool may use.
- `src/gcp_safe_agent_cli/config.py`: `.env` parsing and local settings.
- `src/gcp_safe_agent_cli/http.py`: HTTP client wrapper around `requests`.
- `src/gcp_safe_agent_cli/redaction.py`: redacts secrets, URLs, headers, and sensitive values before output.
- `src/gcp_safe_agent_cli/runs.py`: local run records under `.state/runs/`.
- `src/gcp_safe_agent_cli/audit_log.py`: optional JSONL audit events.
- `src/gcp_safe_agent_cli/json_files.py`: safe JSON reading and writing for plans, inputs, receipts, and outputs.

## How to add or change GCP coverage

Use the generator for Google API operations. Use `commands/` for local helpers such as `auth`, `onboarding`, `inventory` and `runs`.

1. Confirm the official Google source for the service or operation.
2. Update `scripts/generate_gcp_discovery_inventory.py` only if the current generator misses that official source.
3. Regenerate `src/gcp_safe_agent_cli/gcp_discovery_inventory.json` and `docs/api_coverage.md`.
4. Check that the operation appears as an explicit generated `service operation` command.
5. Add or update tests for the generated registry, safety class, risk labels, and docs/wrapper alignment.
6. Keep `docs/proof.md`, examples, and workspace notes honest about local validation and live-account limits.
