# Proof and verification

This page records what was checked on the final source and built Python packages on 2026-08-01. No Spaceship credentials were used, and no request was sent to the provider.

## Source checks

The final source passed these Python 3.12.13 checks:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m ruff check src tests setup.py
PYTHONPATH=src python -m mypy src tests
python -m compileall -q src tests setup.py
```

Results: 65 tests passed. Ruff reported no issues. Mypy reported no issues across 32 source files. Compileall completed successfully.

The behavior tests cover direct parity with the supplied OpenAPI file, the 40-operation parser and coverage ledger, the 38 stable operations, both local HTTP-501 refusals, empty HTTP 204 success, HTTP 202 accepted-for-processing status, safe API path encoding, disabled redirects, exact `authCode` redaction, the official billing-contact field, and opaque private-data write errors. Unique canaries prove that contact, billing, transaction, transfer-code, and private-error values do not reach stdout, saved plans, receipts, run indexes, summaries, or audit logs. Run-ID tests refuse empty values, absolute paths, separators, dot segments, traversal, and symlink escapes before an outside path is created.

The suite also covers the authenticated read-like availability POST, official sold-domain filters and cursor handling, per-operation pagination bounds, automatic and explicit plan/receipt paths, transfer preflight, reliable response/request-derived readbacks and missing-ID fallbacks, the fixed provider host, JSON-only output, missing-auth refusal, and the absence of starter command surfaces.

## Package checks

The final source built these package types successfully:

```bash
python -m build --outdir "$ARTIFACT_DIR"
tar -tzf "$ARTIFACT_DIR/qwayk_spaceship_safe_agent_cli-0.1.0.tar.gz"
unzip -l "$ARTIFACT_DIR/qwayk_spaceship_safe_agent_cli-0.1.0-py3-none-any.whl"
```

The source archive contains the public README, docs, examples, behavior tests, tracked `spaceship` skill wrapper, and production source. The wheel contains the production runtime and executable entry point. Both archives were scanned and contained no private absolute paths, generated run files, caches, local environments, or secret canary values.

Retained starter-only files are excluded from both archives and unreachable from the source parser.

## Clean installed-wheel checks

The exact wheel was installed into a fresh Python 3.12.13 environment outside the source tree:

```bash
python -m venv "$INSTALL_VENV"
"$INSTALL_VENV/bin/python" -m pip install "$ARTIFACT_DIR/qwayk_spaceship_safe_agent_cli-0.1.0-py3-none-any.whl"
cd /tmp
env -u PYTHONPATH "$INSTALL_VENV/bin/qwayk-spaceship-safe-agent-cli" --version
env -u PYTHONPATH "$INSTALL_VENV/bin/qwayk-spaceship-safe-agent-cli" --help
```

The installed package reported version `0.1.0` from the fresh environment, not the source checkout. It registered exactly 40 provider operations: 38 stable and two unavailable. It used only `https://spaceship.dev/api`, exposed only the named operation and local front-door commands, and did not contain excluded starter modules.

Both unavailable commands refused locally with HTTP 501 and no credentials. A stable read and the read-like availability POST with missing authentication returned one valid JSON error document without revealing supplied values. Sold-domain parser checks accepted `take`, `cursor`, and both sale-date filters, with the official 100-item bound. A domain-renewal write request without credentials produced one valid JSON plan without network access and saved it at the automatic run-local path. The plan named the exact domain and reviewed renewal fields, required the spend, ownership, and no-snapshot acknowledgements, and stated that the official API provides no reliable amount, currency, or fee recheck for that operation.

The installed wheel also refused traversal and unsafe run IDs before creating an outside directory. Its persisted command display kept domains readable while hashing contact and SafePay transaction identifiers. Installed fake-transport checks proved that a private-data write error could not expose transfer-code, billing-contact, or opaque provider-error canaries in stdout, its plan, or its receipt. The same check confirmed that redirects stay disabled and the retained starter modules are absent.

## What remains unverified

No live read or write was authorized. Provider responses, account permissions, real prices, rate limits, live async completion, and post-write readback therefore remain unverified. HTTP 202 must still be treated as accepted for processing, not completed.
