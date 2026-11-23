# Azure CLI internals

The CLI packages a command list generated from Microsoft’s Azure REST API specifications. The list keeps the selected operation and API version for each named command.

- `src/azure_safe_agent_cli/official_inventory.json` is the packaged command list.
- `generated_registry.py` loads it for command selection.
- `generated_runtime.py` checks the input, picks the Azure target, and handles previews, approvals and receipts.
- `config.py` reads local settings. `azure_auth.py` selects the Azure CLI or local token connection.
- `http.py` sends the approved request and handles responses. The runtime only uses same-host status links for authenticated status checks.
- `runs.py` and `audit_log.py` keep local run records and audit events.

The generator writes the inventory inside the Python package and updates [the coverage guide](api_coverage.md). See [the approval guide](safety_model.md) for how the tool handles changes.
