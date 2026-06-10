# Architecture

Layers:
- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs (auth/post/media/jobs)
- `wp_api.py`: WordPress REST calls
- `extract.py` / `edit_content.py`: content analysis and safe edits
- `audit_log.py`: JSONL audit events

Goal: add features by adding small verbs, without touching core safety rules.

