# Architecture

Ghost is built as a small command-line tool for posts, pages, members, newsletters, offers, themes, and webhooks. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Ghost.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Ghost."

## Architecture notes

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
