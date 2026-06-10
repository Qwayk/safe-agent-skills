# Architecture

This page is for technical readers who want to inspect how the Amazon Creators tool is organized.
If you just want to use the skill, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Command reference](command_reference.md).

Layers:
- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files
