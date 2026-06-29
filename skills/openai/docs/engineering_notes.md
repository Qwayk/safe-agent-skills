# Engineering notes (curated)

Purpose:
- Capture real problems we hit while building/maintaining this tool and how we solved them.
- Provide “proof of experience” and reduce repeat debugging for customers.

Rules:
- Keep entries short and factual (no hype, no blame).
- Link to the provider doc and public-safe release note where applicable.
- Never include secrets (tokens, client secrets, Authorization headers).

## Entry template

- Date (UTC): note the day in UTC (for example, 2026-03-14)
- Symptom: what failed or why something was confusing during the build
- Root cause: what actually triggered the failure or confusion
- Fix: what code/docs/tests changed to resolve it
- Validation: which commands proved the fix (e.g., `python3 -m unittest -q`)
- References: link to relevant docs/architecture notes
- Release note: short public-safe pointer to the change that captured the fix

## Recent entries

- Date (UTC): 2026-03-14
- Symptom: The OpenAI tool was missing front-door docs/site references and the repo-level proof/coverage indexes did not mention the new CLI.
- Root cause: The tool release added new docs/preset entries after the prior site/AGENTS sync, so the marketing ledgers and `AGENTS` pointers remained stale.
- Fix: Added the OpenAI tool to `api-tools/README.md`, `docs/api_coverage.md`, `docs/proof.md`, `projects/AUTOMATION_CATALOG.md`, the Qwayk pages/index, changelog, and tracking ledgers, plus created a proof artifact and site page draft; reran `sync_tool_docs` to refresh the doc map.
- Validation: `python3 -m unittest -q`, `rg -n "example-api-tool|openai-api-tool" . -S`, `rg -n "\\b(TODO|FIXME|TBD)\\b" . -S --glob '!docs/official_openapi_*'`, plus the `sync_tool_docs.py --apply` run.
- References: `docs/references.md`, `docs/api_coverage.md`
- Release note: captured in the initial OpenAI tool release notes.
- Date (UTC): 2026-03-15
- Symptom: Streaming and binary responses were printed raw, secret values leaked in receipts, and writes could replay without dedupe.
- Root cause: the dispatcher only trimmed response text, didn’t redact JSON secrets, and did not have a documented idempotency header.
- Fix: added streaming-to-file support, binary artifacts, JSON redaction, and a plan-drift refusal instead of relying on an undocumented idempotency header; updated the safety model, references, and tests; receipts now record the artifact metadata instead of raw bytes.
- Validation: `python3 -m unittest -q`
- References: `docs/safety_model.md`, `docs/references.md`
- Release note: captured in the OpenAI tool safety hardening notes.
