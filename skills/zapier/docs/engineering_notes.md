# Engineering notes

## Where to make changes

- `src/zapier_safe_agent_cli/operations_data.json` lists the named commands. Update it with [API coverage](api_coverage.md) and the [command reference](command_reference.md) when a command changes.
- `cli.py` builds the parser, checks saved plans, sends requests, and writes receipts. `config.py` reads settings, and `http.py` sends requests.
- `runs.py` and `audit_log.py` record local results. Check how any new output or saved field handles credentials and private inputs.
- `pyproject.toml` puts the operation list in the install. `MANIFEST.in` keeps the skill and docs in the source archive.

Keep the [original API files](references.md) in place. Add only named commands for documented operations. For a change, check the plan before any request and make the receipt say what Zapier actually confirmed. Use simulated replies in tests. Verify a fresh install outside the checkout as described in [the test record](proof.md).
