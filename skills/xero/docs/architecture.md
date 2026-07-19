# Architecture

The CLI is data-driven, but not generic. The packaged catalog defines 474 fixed names and their exact Xero method, URL, parameters, scopes, region, auth flow, access limits, and safety behavior.

## Main parts

- `openapi_inventory.py` reads the pinned official YAML files, adds the small official manual supplement, classifies compatibility and access limits, and renders the catalog and coverage ledger.
- `generated/operations.json` is the packaged fixed-command catalog. Its exact SHA-256, count, commit, servers, methods, command names, paths, and path-parameter bindings are checked at load time.
- `registry.py` exposes exact command descriptions and minimum-scope unions.
- `cli.py` creates one argparse command for every callable catalog row and handles setup, auth, tenant, and inventory helpers.
- `auth.py` implements PKCE, token exchange and refresh, separate client-credentials profiles, and secret-free status.
- `tenants.py` stores exact PKCE tenant selection and exact Custom Connection organisation discovery.
- `runtime.py` validates fixed input, protects reads, binds uploaded file bytes into write plans, applies reviewed plans, verifies, and writes receipts.
- `http.py` is the only provider transport. It retries reads on documented transient statuses and never logs headers or bodies.
- `redaction.py`, `state.py`, and `output.py` enforce secret-safe output, protected local files, and one-object JSON stdout.

## Request flow

For a fixed command, the runtime loads the packaged row, validates the input contract, reads the correct token profile, loads the exact tenant when required, checks scope and region, then either performs a read or enters the write-plan flow. It never accepts an arbitrary method, host, path, or endpoint.

## Generated boundary

Run the generator only against a Git checkout at the pinned commit:

```bash
.venv/bin/python scripts/generate_xero_inventory.py \
  --spec-root /path/to/Xero-OpenAPI-at-the-pinned-commit
```

The generator refuses a different commit or release, any changed pinned source-file hash, a changed webhook path shape, duplicate command names, or a changed 477-operation OpenAPI count. Runtime loading also refuses any change to the committed catalog hash.
