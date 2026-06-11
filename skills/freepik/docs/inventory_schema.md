# Inventory schema (inventory CSV)

The inventory CSV is the local license ledger written by approved Freepik downloads. Licensed apply still requires explicit no-snapshot approval before writing rows when no saved snapshot is available.

Columns:
- `downloaded_at_utc`: timestamp of download
- `resource_id`: Freepik resource id
- `resource_type`: best-effort from detail response
- `title`: best-effort from detail response
- `author`: best-effort from detail response
- `resource_url`: best-effort from detail response
- `preview_url`: best-effort (only when clearly present)
- `download_url`: URL used to fetch the binary
- `license_url`: URL of the license PDF (required)
- `download_id`: reserved for future use if API returns a download/transaction id
- `format`: requested format (e.g., `jpg`)
- `image_size`: requested image resize (e.g., `2000px`) when used
- `file_name`: saved filename
- `file_path`: saved path
- `sha256`: file digest
- `keywords`: best-effort semicolon-separated list from resource detail tags, when present
- `post_slug`: optional Ghost post slug this download is for
- `ghost_id`: optional Ghost post id this download is for
- `usage_role`: optional usage role (`featured` or `body`)
- `tags`: optional manual tags (free-form)
- `notes`: free-form
