# What this build proves

## Proved without Jira credentials

- Both pinned official files match their tracked SHA-256 hashes.
- The files contain 616 Platform operations and 105 Software operations: 721 unique method-and-path rows with no overlap.
- Deterministic generation produces the packaged fixed-command inventory, manifest, and complete coverage ledger.
- Every row has one fixed command name and an implemented, gated, preview, deprecated, OAuth-only, or intentional product-boundary status.
- Gated rows refuse before HTTP. There is no arbitrary method, URL, raw-request, SDK, or OpenAPI pass-through command.
- Mocked reads cover Basic and OAuth request behavior without leaking credentials.
- Mocked writes cover locally signed dry-run plans, recomputed-hash tamper refusal across every request and safety field, file-drift refusal, snapshot success and failure, no-snapshot approval, high-risk approval, verification, and private redacted receipts.
- Target tests prove Basic and OAuth credentials refuse non-Jira hosts, wrong gateway paths, and custom production ports before HTTP.
- The 360-write invariant recomputes the auditable stronger-approval reasons for every row; 277 writes require the extra approval. A named invariant covers all seven reviewed project-administration commands, and a CLI behavior test proves `create-component` apply refuses before HTTP without `--ack-high-risk`.
- JSON success, refusal, and error paths emit one JSON object.
- Wrapper tests locate and validate either the source `skills/jira/SKILL.md` or the published top-level `SKILL.md`, and fail when neither layout exists.
- Source tests, Ruff, mypy, source and wheel builds, clean-wheel installation, and installed inventory and safety checks pass when recorded below.

## Not proved live

No real Jira credential was used and no Jira site was called. Real tenant permissions, user roles, Jira product plans, OAuth scopes, rate limits, attachment limits, async task behavior, provider error bodies, and live write results remain unverified. The tool and coverage ledger say this directly instead of treating mocked behavior as provider proof.

## Verification record

Run on 2026-07-27 with bundled Python 3.12.13:

- `.venv/bin/ruff check src tests generate_inventory.py` — passed.
- `.venv/bin/mypy src` — passed for 13 source files.
- `.venv/bin/python -m unittest -q` — 42 tests passed, including fixed-plan construction for all 687 supported-auth rows, target restriction, eight recomputed-hash tamper cases, private signing keys, full stronger-approval invariants, the seven project-administration commands and representative refusal, preserved Jira pagination cursors, and default output and audit redaction of other token-shaped fields.
- Deterministic regeneration — the combined SHA-256 of `specs/manifest.json`, packaged `operations.json`, and `docs/api_coverage.md` stayed `2e0d3d5fc4a002b219c65452d69a5d1975b21ed786a0915c9e0b5900d3cea18b` before and after generation.
- `.venv/bin/python -m build` — source and wheel builds passed.
- The wheel contains the packaged inventory and no starter package. The source archive contains both pinned descriptions, generator, docs, examples, wrapper, and test helpers.
- A clean Python 3.12 virtual environment installed the built wheel outside the source checkout. Its installed module came from `site-packages`, loaded the `721`/`687` boundary and `277` stronger-approval count, created mode-`0600` plans and signing keys, and refused an arbitrary Basic host, recomputed plan tampering, a project-administration apply without its stronger approval, and a Forge-only command before HTTP.
- The mechanically refreshed local public mirror passed Ruff, mypy, and the same 42 tests from its own `src`. Its top-level `SKILL.md` matched the source wrapper, all relative links resolved, and cache, generated/private-file, private-path, secret, catalog-row, and whitespace checks passed.

This record does not claim live Jira proof. Keep the unverified limits above until an authorized real-account test exists.
