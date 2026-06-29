# Architecture

This page is for builders who need to understand where the code lives before changing it.

Read this after the user-facing docs, not before them.

## Main parts

- `cli.py`: argument parsing, shared flags, local run artifacts, and command registration.
- `gemini_commands.py`: generated Gemini family/method command wiring.
- `operation_registry.py`: 82 explicit operations from the pinned `v1beta` and `v1` discovery docs.
- `gemini_runtime.py`: request building, API-key redaction, dry-run plans, reviewed applies, and receipts.
- `config.py`: `.env` parsing for `GEMINI_API_KEY`, `GEMINI_API_BASE_URL`, and timeout.
- `audit_log.py`: optional JSONL audit events.
- `runs.py`: local run artifacts and history index under `.state/runs/`.
- `json_files.py`: safe JSON read/write helpers for plan and receipt files.
