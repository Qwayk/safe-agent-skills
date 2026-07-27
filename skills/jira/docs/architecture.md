# Architecture

`generate_inventory.py` verifies the SHA-256 hash and operation count of both pinned OpenAPI descriptions. It writes three deterministic files: `specs/manifest.json`, the packaged `operations.json`, and `docs/api_coverage.md`.

At runtime, `cli.py` creates one argparse subcommand for every inventory row. Each parser exposes only that operation's documented path, query, non-auth header, body, multipart, and response-file inputs. Authorization and cookie headers are never command inputs; `http.py` owns configured authentication. `operations.py` resolves the fixed request, enforces coverage and auth gates, creates and validates write plans, checks referenced file hashes, performs snapshots and readback when available, and writes private receipts. The HTTP client also owns timeouts, retries for reads, and secret-safe errors.

Gated, experimental, and intentionally excluded rows remain named in the inventory and CLI. They refuse before network access, which keeps the official boundary fully accounted without pretending unsupported credentials work.
