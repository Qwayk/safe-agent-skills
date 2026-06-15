# Architecture

WordPress is built as a small command-line tool for posts, pages, media, users, comments, settings, and plugin-related checks. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches WordPress.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for WordPress."

## Runtime layers

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs (auth/post/media/jobs)
- `wp_api.py`: WordPress REST calls
- `extract.py` / `edit_content.py`: content analysis and safe edits
- `audit_log.py`: JSONL audit events

Goal: add features by adding small verbs, without touching core safety rules.
