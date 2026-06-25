# Architecture

The Google Cloud skill is built as a small command-line tool with a generated command registry, a shared runtime, local safety checks, and Google Application Default Credentials for access. This matters when an agent is using the skill for real work. A reviewer can see where commands come from, where input is checked, where plans and receipts are written, and why broad Google Cloud operations should not be added by hand.

A good architecture check is: confirm the operation comes from the generated inventory, then check that the shared runtime still handles input, target allowlists, dry-run plans, apply gates, redaction, and receipt output.

Read this after the user-facing docs, not before them. Most GCP provider operations are generated from official Google sources; do not add one-off command modules for normal Google Cloud operations. The normal Google Cloud operations come from the official-source generator.

## Runtime

The source boundary starts in `docs/_generated/gcp_discovery_inventory.json`. That file records the included services, generated operations, path templates, safety classes, risk labels, and official source evidence.

`src/gcp_safe_agent_cli/generated_registry.py` packages that inventory for the runtime. `src/gcp_safe_agent_cli/generated_runtime.py` turns each row into an explicit `service operation` command, validates the input JSON, builds the Google request, applies safety gates, writes dry-run plans, and records receipts.

The command shape is always:

```bash
qwayk-gcp-safe-agent-cli <service> <operation> --input-json input.json
```

There is no raw request bridge and no arbitrary URL caller.

## Main files

- `scripts/generate_gcp_discovery_inventory.py`: rebuilds the official-source inventory and coverage docs.
- `docs/_generated/gcp_discovery_inventory.json`: generated source boundary used by the runtime.
- `docs/api_coverage.md`: human-readable coverage ledger and command lookup table.
- `src/gcp_safe_agent_cli/cli.py`: global flags, built-in commands, and generated service registration.
- `src/gcp_safe_agent_cli/generated_registry.py`: packaged service and operation registry.
- `src/gcp_safe_agent_cli/generated_runtime.py`: generated command execution, plan/apply checks, request construction, and receipt shape.
- `src/gcp_safe_agent_cli/google_auth.py`: Google Application Default Credentials and quota-project handling.
- `src/gcp_safe_agent_cli/project_config.py`: project, folder, organization, billing account, region, zone, and `locations/...` allowlist checks.
- `src/gcp_safe_agent_cli/config.py`: `.env` parsing and local settings.
- `src/gcp_safe_agent_cli/http.py`: HTTP client wrapper around `requests`.
- `src/gcp_safe_agent_cli/redaction.py`: redacts secrets, URLs, headers, and sensitive values before output.
- `src/gcp_safe_agent_cli/runs.py`: local run records under `.state/runs/`.
- `src/gcp_safe_agent_cli/audit_log.py`: optional JSONL audit events.
- `src/gcp_safe_agent_cli/json_files.py`: safe JSON reading and writing for plans, inputs, receipts, and outputs.

## How to add or change GCP coverage

Use official Google sources first. For normal provider operations, update the generator and rebuild the inventory. Do not hand-add a one-off command under `commands/` to make a missing Google Cloud operation appear covered.

The safe path is:

1. Confirm the official Google source for the service or operation.
2. Update `scripts/generate_gcp_discovery_inventory.py` only if the current generator misses that official source.
3. Regenerate `docs/_generated/gcp_discovery_inventory.json` and `docs/api_coverage.md`.
4. Check that the operation appears as an explicit generated `service operation` command.
5. Add or update tests for the generated registry, safety class, risk labels, and docs contract.
6. Keep `docs/proof.md`, examples, and workspace notes honest about local validation and live-account limits.

Manual command modules are only for local helper commands such as `auth`, `onboarding`, `inventory`, and `runs`, not for broad GCP provider coverage.
