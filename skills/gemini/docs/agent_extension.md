# Agent Extension Guide

Use this page when changing the Gemini source tool.

## Where Behavior Lives

- `docs/official_discovery_v1beta.json` and `docs/official_discovery_v1.json`: pinned official API source.
- `docs/official_inventory.json`: normalized inventory.
- `src/gemini_api_tool/operation_registry.py`: generated command registry.
- `src/gemini_api_tool/gemini_commands.py`: parser registration for explicit command families.
- `src/gemini_api_tool/gemini_runtime.py`: request building, redaction, dry-run plans, applies, and receipts.

## Rules

- Do not add raw request, generic REST, SDK-pass-through, or OpenAI-compatible bridge commands.
- Keep command names aligned with `docs/api_coverage.md`.
- Keep `GEMINI_API_KEY` redacted in output, logs, plans, and receipts.
- Add tests before changing command behavior.
- If discovery is refreshed, update pinned docs, `official_inventory.json`, `operation_registry.py`, `docs/api_coverage.md`, `docs/proof.md`, and tests together.
