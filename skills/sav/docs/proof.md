# Proof and verification

## Last verified

- Date (UTC): 2026-07-31
- Runtime: `sav` CLI
  - Version: `0.1.4`
- Fixed runtime host: `https://api.sav.com/domains_api_v1/`
- Provider API source: `https://documenter.getpostman.com/view/9688716/TzzANHFJ`

## What this proves

- The vendored collection matches the pinned SHA-256 and deterministically generates 12 commands.
- Mocked behavior tests cover all 12 dispatch paths, the fixed host and `APIKEY` header, redirect refusal, zero-network dry-runs, plan key creation, HMAC signing, approvals, useful redaction, strict validation, apply-attempt outcomes, safe errors, receipts, and wrapper layout contract checks (source/public exclusivity with missing+duplicate fail cases).
- Ruff and mypy pass for the current source.
- No restore or rollback contract exists for this boundary.

## Verified results

- Vendored collection SHA-256: `d330b3df8f1b1962fcae295b0dc47b831c15f68d0d90db73c4dcb151968e33fe`.
- Deterministic generation: current.
- Unit tests: all `50` pass in the source layout and in a fresh public-style layout.
- Ruff: clean.
- Mypy: clean across `11` source files.
- Example JSON: all `3` files parse.
- Source archive and wheel: exact version `0.1.4` built successfully.
- Archive/privacy checks: current wheel and source archive are clean.
- Clean installed-wheel proof: version `0.1.4`, exact 12-operation/4-read/8-write inventory.

## Smoke checks

Run these checks from the tool folder:

```bash
.venv/bin/python -m json.tool docs/examples/read-active.example.json
.venv/bin/python -m json.tool docs/examples/plan.example.json
.venv/bin/python -m json.tool docs/examples/receipt.example.json
.venv/bin/python tools/generate_inventory.py --check
PYTHONPATH=src .venv/bin/python -m unittest -q
PYTHONPATH=src .venv/bin/ruff check src tests tools
PYTHONPATH=src .venv/bin/mypy src
```

## Proof notes

- Write dry-runs are local, make no provider request, and save a mode-`0600` plan.
- apply requires reviewed plan + all explicit approval flags.
- independent readback and rollback are not available for current writes.
- `provider_response_only` is true only when `provider_response_received` is true.
- `durable_state_verified` stays false on every current path because no independent SAV readback exists.
- `receipt_written` reports only whether the local receipt was saved.
- a 2xx response is reported as `provider_accepted`; it is not verified lasting SAV account state.
- on every non-2xx provider response, apply returns `1` and writes a redacted receipt when the final private write succeeds.
- pre-transport receipt failure stops before network; request exceptions keep the outcome unknown; final receipt persistence failure keeps the provider status visible and says not to retry blindly.
- the JSON examples are mocked, redacted illustrations only. They are not live SAV responses and do not contain real signatures or private paths.
- No credential or live SAV request was used for this proof.

## Output artifacts in this repo

- `docs/examples/read-active.example.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`
- `docs/api_coverage.md` (generator output)

## Layout coverage

- Source layout: the complete suite passes with only `skills/sav/SKILL.md`.
- Public layout: the complete suite passes in a fresh temporary public-style copy with only top-level `SKILL.md` and no `skills/` tree.
- The resolver rejects a missing wrapper and rejects both paths together, so one layout cannot silently duplicate or lose the wrapper behavior.
