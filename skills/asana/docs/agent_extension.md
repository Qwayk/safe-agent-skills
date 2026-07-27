# Maintaining the generated Asana boundary

Do not hand-add a provider path or command. The only supported extension path begins with a reviewed official Asana OpenAPI input.

## Update the pinned specification

1. Review the official `Asana/openapi` commit and confirm the product boundary still excludes App Components, SCIM, and arbitrary batch execution.
2. Replace `specs/asana_oas.yaml` with the exact pinned `defs/asana_oas.yaml` file.
3. Update the commit and expected SHA-256 in `scripts/generate_inventory.py` and the references page.
4. Run `.venv/bin/python scripts/generate_inventory.py`.
5. Inspect added, removed, or changed operations before accepting generated files.

## Review runtime effects

For each changed operation, check:

- command-name collisions
- path and query parameters
- JSON or multipart body shape
- OAuth scope and service-account or plan notes
- read versus write classification
- stronger-risk reasons
- same-path snapshot and verification suitability
- pagination, event stream, webhook handshake, export, and job behavior
- binary or file handling

Keep operation-specific restrictions in the shared runtime only when the fixed spec metadata cannot express them. The attachment `connect_to_app` refusal is one example because that field crosses into the excluded App Components boundary.

## Required checks

```bash
.venv/bin/python scripts/generate_inventory.py --check
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/python -m unittest -q
.venv/bin/python -m build
```

Then install the wheel into a clean Python 3.12 environment and confirm the packaged inventory, CLI, tests from source, and fixed command discovery still work. Update coverage, command docs, wrapper, examples, proof, and the changelog in the same change.
