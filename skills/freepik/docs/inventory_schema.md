# Inventory CSV

The inventory CSV records the files and licenses from approved Freepik downloads. Each completed row includes the saved file, a SHA-256 hash and the license link. The column order stays the same.

## Columns
- `downloaded_at_utc`: timestamp of download
- `resource_id`: Freepik resource id
- `resource_type`: from the asset details when available
- `title`: from the asset details when available
- `author`: from the asset details when available
- `resource_url`: from the asset details when available
- `preview_url`: preview link when available
- `download_url`: URL used to fetch the binary
- `license_url`: license link (required)
- `download_id`: download ID when Freepik provides one
- `format`: format of the saved file, such as `jpg` or `png`
- `image_size`: requested image resize (e.g., `2000px`) when used
- `file_name`: saved filename
- `file_path`: saved path
- `sha256`: file digest
- `keywords`: asset keywords separated by semicolons, when available
- `post_slug`: optional Ghost post slug this download is for
- `ghost_id`: optional Ghost post id this download is for
- `usage_role`: optional usage role (`featured` or `body`)
- `tags`: optional manual tags (free-form)
- `notes`: free text. When the returned file has a different format, new rows include `requested_format=...` so the tool can still spot a repeat download.
