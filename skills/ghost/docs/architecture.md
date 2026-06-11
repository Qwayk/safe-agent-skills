# Architecture (high level)

`ghost-api-tool` is split into small layers:

1) CLI layer (`ghost_api_tool/cli.py`)
   - Parses args, builds context, routes to command handlers.

2) API layer (`ghost_api_tool/ghost_api.py`)
   - Generates Admin API JWT.
   - Performs authenticated requests with required headers.

3) Safety engine (`ghost_api_tool/post_patch.py`)
   - Implements the safe update loop:
     - GET latest
     - merge
     - PUT with `updated_at`
     - GET verify
   - Used for field-level updates (status, feature image, metadata).
   - Post-body transforms use a specialised idempotence verification.

4) Content transforms
   - HTML card mode: `ghost_api_tool/content_html_card.py`
   - Lexical mode (normal posts): `ghost_api_tool/content_lexical.py`
   - Post-body transforms use an idempotence verification (re-running the transform must be a no-op).

5) Read-only inventories + safe cleanup
   - Tags: `ghost_api_tool/commands/tag.py` + `ghost_api_tool/ghost_api.py` (`/admin/tags/`)
   - Bulk cleanup commands follow the same safety pattern:
     - Dry-run by default
     - Require explicit `--apply` (and `--yes` for bulk)
     - Verify by read-back (e.g., deleted resources return 404)

This layout keeps moving parts minimal and concentrates safety logic in one place.
